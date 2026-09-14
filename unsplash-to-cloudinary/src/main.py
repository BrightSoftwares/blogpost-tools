#!/usr/bin/env python3
"""
Unsplash -> Cloudinary blog image pipeline.

Reads markdown files with frontmatter, searches Unsplash for a matching
image (image_search_query / silot_terms), uploads the chosen photo to
Cloudinary, and writes the resulting Cloudinary URL back into the
frontmatter's `image` field.

Rewritten for:
  - explicit Cloudinary credential handling (fixes silent 401s)
  - structured logging instead of scattered prints
  - no more swallowed exceptions (pandas .append removed in 2.0, etc.)
  - HTTP status/error-body checking on every external call
"""

import os
import sys
import logging
import urllib.parse

import frontmatter
import pandas as pd
import requests
import cloudinary
import cloudinary.uploader


# --------------------------------------------------------------------------
# Logging setup
# --------------------------------------------------------------------------

def setup_logging():
    level_name = os.getenv("INPUT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("unsplash_to_cloudinary")


log = setup_logging()


# --------------------------------------------------------------------------
# Cloudinary configuration
# --------------------------------------------------------------------------

def configure_cloudinary():
    """
    Explicitly configure the Cloudinary SDK instead of relying on it to
    pick up CLOUDINARY_URL implicitly. This is almost certainly the cause
    of the 401: cloudinary.config(secure=True) alone does NOT guarantee
    credentials are loaded, depending on when/how CLOUDINARY_URL is set
    in the Action's environment.

    IMPORTANT: this is a GitHub Actions *docker* action. Inputs declared in
    action.yml (e.g. `cloudinary_url:`) are injected by GitHub as env vars
    named INPUT_<NAME_UPPERCASED> — i.e. INPUT_CLOUDINARY_URL, NOT
    CLOUDINARY_URL. Reading the bare CLOUDINARY_URL name (as the original
    script did) will always return None in this container, silently
    configure Cloudinary with empty credentials, and produce a 401 on
    upload. We read INPUT_CLOUDINARY_URL first and fall back to a bare
    CLOUDINARY_URL only for local/non-Action runs.
    """
    cloudinary_url = os.getenv("INPUT_CLOUDINARY_URL") or os.getenv("CLOUDINARY_URL")

    if cloudinary_url:
        config = cloudinary.config(cloudinary_url=cloudinary_url, secure=True)
        log.info("Cloudinary configured via INPUT_CLOUDINARY_URL/CLOUDINARY_URL.")
    else:
        cloud_name = os.getenv("INPUT_CLOUDINARY_CLOUD_NAME") or os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("INPUT_CLOUDINARY_API_KEY") or os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("INPUT_CLOUDINARY_API_SECRET") or os.getenv("CLOUDINARY_API_SECRET")

        if not all([cloud_name, api_key, api_secret]):
            log.error(
                "Cloudinary credentials are missing. In action.yml this should "
                "come through as the 'cloudinary_url' input (exposed to this "
                "container as INPUT_CLOUDINARY_URL, in the form "
                "cloudinary://<api_key>:<api_secret>@<cloud_name>). Make sure "
                "the calling workflow passes `with: cloudinary_url: "
                "${{ secrets.CLOUDINARY_URL }}` (or equivalent)."
            )
            raise RuntimeError("Missing Cloudinary credentials")

        config = cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        log.info("Cloudinary configured via discrete env vars.")

    # Sanity-check what actually got loaded (never log the secret itself)
    log.debug(
        "Cloudinary config -> cloud_name=%s api_key_set=%s api_secret_set=%s",
        config.cloud_name,
        bool(config.api_key),
        bool(config.api_secret),
    )

    if not config.cloud_name or not config.api_key or not config.api_secret:
        log.error(
            "Cloudinary config resolved but one or more fields are empty "
            "(cloud_name=%r, api_key_set=%s, api_secret_set=%s). "
            "This will cause a 401 on upload.",
            config.cloud_name, bool(config.api_key), bool(config.api_secret),
        )
        raise RuntimeError("Incomplete Cloudinary credentials")

    return config


# --------------------------------------------------------------------------
# Unsplash search
# --------------------------------------------------------------------------

def get_unsplash_results_dataframe(obj_array):
    return pd.DataFrame(obj_array, columns=["query", "photo_id", "photo_link"])


def load_or_create_results_file(results_file):
    if os.path.exists(results_file):
        log.info("Loading existing results file: %s", results_file)
        return pd.read_csv(results_file)
    log.info("Results file %s not found. Creating an empty one.", results_file)
    df = get_unsplash_results_dataframe([])
    df.to_csv(results_file, index=False)
    return df


def search_unsplash_image(query, api_access_key, results_file, max_results):
    results_df = pd.read_csv(results_file)

    existing_result_df = results_df[results_df["query"] == query]

    if not existing_result_df.empty:
        log.info("Found cached Unsplash results for query %r.", query)
        return existing_result_df

    log.info("No cached results for %r. Querying Unsplash API.", query)

    encoded_query = urllib.parse.quote(query)
    url = (
        "https://api.unsplash.com/search/photos"
        f"?page=1&query={encoded_query}&client_id={api_access_key}"
        f"&orientation=landscape&per_page={max_results}"
    )

    try:
        resp = requests.get(url, timeout=30)
    except requests.RequestException as e:
        log.error("Network error calling Unsplash for query %r: %s", query, e)
        return get_unsplash_results_dataframe([])

    if resp.status_code == 401:
        log.error(
            "Unsplash returned 401 Unauthorized for query %r. "
            "Check INPUT_UNSPLASH_ACCESS_KEY is set and valid. Body: %s",
            query, resp.text[:500],
        )
        return get_unsplash_results_dataframe([])

    if not resp.ok:
        log.error(
            "Unsplash search failed (status=%s) for query %r. Body: %s",
            resp.status_code, query, resp.text[:500],
        )
        return get_unsplash_results_dataframe([])

    data = resp.json()
    results = data.get("results", [])
    log.info("Unsplash returned %d result(s) for query %r.", len(results), query)

    rows = [
        [query, photo["id"], photo["links"]["download"]]
        for photo in results
        if "id" in photo and "links" in photo and "download" in photo["links"]
    ]

    new_results_df = get_unsplash_results_dataframe(rows)
    save_unsplash_search(new_results_df, results_file)
    return new_results_df


def save_unsplash_search(results_df, dest_file):
    log.debug("Saving %d new Unsplash result row(s) to %s", len(results_df), dest_file)
    existing_df = load_or_create_results_file(dest_file)
    combined_df = pd.concat([existing_df, results_df], ignore_index=True)
    combined_df.drop_duplicates(inplace=True)
    combined_df.to_csv(dest_file, index=False)


def find_best_item(results_df, used_vids_df):
    if results_df.empty:
        log.warning("No Unsplash results to choose from.")
        return None

    used_ids = used_vids_df["item_id"] if "item_id" in used_vids_df.columns else []
    unused_df = results_df[~results_df["photo_id"].isin(used_ids)]

    if unused_df.empty:
        log.warning("All %d candidate photo(s) were already used.", len(results_df))
        return None

    log.info("Selected photo_id=%s from %d unused candidate(s).",
              unused_df.iloc[0]["photo_id"], len(unused_df))
    return unused_df.head(1)


# --------------------------------------------------------------------------
# Cloudinary upload
# --------------------------------------------------------------------------

def upload_image_to_cloudinary(photo_id, photo_link, cloudinary_dest_folder, cloudinary_transformation):
    log.info("Uploading photo_id=%s to Cloudinary folder=%s", photo_id, cloudinary_dest_folder)
    try:
        upload_response = cloudinary.uploader.upload(
            photo_link,
            folder=cloudinary_dest_folder,
            public_id=photo_id,
            unique_filename=False,
            overwrite=True,
        )
    except cloudinary.exceptions.AuthorizationRequired as e:
        log.error(
            "Cloudinary 401 Unauthorized while uploading photo_id=%s. "
            "Credentials are being sent but rejected — double-check the "
            "API key/secret/cloud_name match the target Cloudinary account "
            "and that the key hasn't been rotated/revoked. Details: %s",
            photo_id, e,
        )
        raise
    except cloudinary.exceptions.Error as e:
        log.error("Cloudinary API error uploading photo_id=%s: %s", photo_id, e)
        raise
    except requests.RequestException as e:
        log.error("Network error uploading photo_id=%s to Cloudinary: %s", photo_id, e)
        raise

    public_id = upload_response.get("public_id")
    log.info("Upload succeeded. public_id=%s", public_id)

    src_url = cloudinary.CloudinaryImage(public_id).build_url(
        transformation=[cloudinary_transformation]
    )
    log.info("Built delivery URL: %s", src_url)
    return src_url


# --------------------------------------------------------------------------
# Main pipeline
# --------------------------------------------------------------------------

def process_entry(entry, folder, destination_folder, api_access_key,
                   results_file, used_vids_df, cloudinary_dest_folder,
                   cloudinary_transformation, max_results):
    entry_path = os.path.join(folder, entry)
    log.info("Processing entry: %s", entry)

    post = frontmatter.load(entry_path)
    image_search_query = post.get("image_search_query") or post.get("silot_terms")
    image = post.get("image")

    if image not in (None, "null") or not image_search_query:
        log.info(
            "Skipping %s (image already set=%r, image_search_query=%r).",
            entry, image, image_search_query,
        )
        return None

    search_results = search_unsplash_image(
        image_search_query, api_access_key, results_file, max_results
    )

    best_item_df = find_best_item(search_results, used_vids_df)
    if best_item_df is None:
        log.warning(
            "No image found for %s (query=%r). Leaving frontmatter unchanged.",
            entry, image_search_query,
        )
        return None

    photo_id = best_item_df.iloc[0]["photo_id"]
    photo_link = best_item_df.iloc[0]["photo_link"]

    try:
        cloudinary_image_url = upload_image_to_cloudinary(
            photo_id, photo_link, cloudinary_dest_folder, cloudinary_transformation
        )
    except Exception:
        log.error("Upload failed for %s (photo_id=%s). Not modifying frontmatter.",
                   entry, photo_id)
        return None

    post["image"] = cloudinary_image_url
    with open(entry_path, "w") as f:
        f.write(frontmatter.dumps(post))
    log.info("Updated frontmatter image for %s -> %s", entry, cloudinary_image_url)

    if destination_folder:
        dst_path = os.path.join(destination_folder, entry)
        os.rename(entry_path, dst_path)
        log.info("Moved %s -> %s", entry_path, dst_path)

    return photo_id


def unsplash_to_cloudinary(folder, api_access_key, results_file, already_used_csv,
                            cloudinary_dest_folder, cloudinary_transformation,
                            max_results=10, destination_folder=None):

    configure_cloudinary()

    try:
        used_vids_df = pd.read_csv(already_used_csv)
    except FileNotFoundError:
        log.info("No existing 'already used' file at %s, starting fresh.", already_used_csv)
        used_vids_df = pd.DataFrame(columns=["item_id"])

    load_or_create_results_file(results_file)

    entries = sorted(os.listdir(folder))
    log.info("Found %d entr(y/ies) in %s", len(entries), folder)

    newly_used_ids = []
    for entry in entries:
        try:
            used_id = process_entry(
                entry, folder, destination_folder, api_access_key,
                results_file, used_vids_df, cloudinary_dest_folder,
                cloudinary_transformation, max_results,
            )
            if used_id is not None:
                newly_used_ids.append(used_id)
                used_vids_df = pd.concat(
                    [used_vids_df, pd.DataFrame([used_id], columns=["item_id"])],
                    ignore_index=True,
                )
        except Exception:
            log.exception("Unhandled error while processing entry %r. Skipping it.", entry)

    used_vids_df.drop_duplicates(inplace=True)
    used_vids_df.to_csv(already_used_csv, index=False)
    log.info(
        "Done. %d image(s) newly used this run. Total tracked used images: %d.",
        len(newly_used_ids), len(used_vids_df),
    )


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def require_env(name):
    value = os.getenv(name)
    if not value:
        log.error("Required environment variable %s is not set.", name)
        sys.exit(1)
    return value


if __name__ == "__main__":
    folder = require_env("INPUT_SRC_FOLDER")
    destination_folder = os.getenv("INPUT_DST_FOLDER") or None
    unsplash_access_key = require_env("INPUT_UNSPLASH_ACCESS_KEY")
    already_used_items = require_env("INPUT_ALREADY_USED_ITEMS")
    results_file = require_env("INPUT_SEARCH_RESULTS_FILE")
    max_results = int(os.getenv("INPUT_MAX_RESULTS", "30"))
    cloudinary_dest_folder = os.getenv("INPUT_CLOUDINARY_DESTFOLDER", "blog")
    cloudinary_transformation = os.getenv("INPUT_CLOUDINARY_TRANSFORMATION", "BlogImage")

    log.info(
        "Starting run: src_folder=%s dst_folder=%s cloudinary_folder=%s max_results=%d",
        folder, destination_folder, cloudinary_dest_folder, max_results,
    )

    try:
        unsplash_to_cloudinary(
            folder, unsplash_access_key, results_file, already_used_items,
            cloudinary_dest_folder, cloudinary_transformation,
            max_results, destination_folder,
        )
    except Exception:
        log.exception("Fatal error, aborting run.")
        sys.exit(1)
