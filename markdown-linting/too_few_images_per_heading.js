const {
    forEachLine,
    getLineMetadata,
    inlineCommentStartRe,
    } = require("markdownlint-rule-helpers");
    
    const start_highlight = /{% highlight \w+ %}/;
    const end_highlight = "{% endhighlight %}";
    const max_nb_headings = 2;

    const tooFewImagesPerHeadings = (params, onError) => {
    let insideHighlightBlock = false;
    let nbHeadings = 0;
    let imageFound = false;
    
    forEachLine(getLineMetadata(params), (line, lineIndex) => {
        // if this is a heading increase the count
        const isHeading = true;
        if (line && isHeading) {
          //insideHighlightBlock = true;
          nbHeadings = nbHeadings + 1;
        }

        // if we encounter am image, we reset all the counters
        imageFound = true;
        if (line && imageFound) {
          //insideHighlightBlock = false;
          // reset the nb of headings
          nbHeadings = 0;
        }
      
        //const isComment = line.startsWith("<!--"); // inlineCommentStartRe.test(line);
        //console.log("This is a comment ? " + isComment + ", insideHighlightBlock " + insideHighlightBlock  + ", line =" + line);
        //console.log("");

        // if the nb of headers is already above the limit and we encounter another one, we generate an error
        // and we reset the counters
        if (nbHeadings >= max_nb_headings) {
            onError({
                lineNumber: lineIndex,
            });
        }
    });
    };
    
    module.exports = {
    names: ["CMD002", "too-few-images-per-heading"],
    description: "You should have an image every " + max_nb_headings + " headings",
    tags: ["test", "image_in_post"],
    function: tooFewImagesPerHeadings,
    };
