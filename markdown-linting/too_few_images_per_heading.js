const {
    forEachLine,
    getLineMetadata,
    inlineCommentStartRe,
    } = require("markdownlint-rule-helpers");
    
    const start_highlight = /{% highlight \w+ %}/;
    const end_highlight = "{% endhighlight %}";
    const max_nb_headings = 2;
    let nbHeadings = 0;
    let imageFound = false;

    // const tooFewImagesPerHeadings = (params, onError) => {
    // let insideHighlightBlock = false;
    
    // forEachLine(getLineMetadata(params), (line, lineIndex) => {
    //     // if this is a heading increase the count
    //     const isHeading = true;
    //     if (line && isHeading) {
    //       //insideHighlightBlock = true;
    //       nbHeadings = nbHeadings + 1;
    //     }

    //     // if we encounter am image, we reset all the counters
    //     imageFound = true;
    //     if (line && imageFound) {
    //       //insideHighlightBlock = false;
    //       // reset the nb of headings
    //       nbHeadings = 0;
    //     }
      
    //     //const isComment = line.startsWith("<!--"); // inlineCommentStartRe.test(line);
    //     //console.log("This is a comment ? " + isComment + ", insideHighlightBlock " + insideHighlightBlock  + ", line =" + line);
    //     //console.log("");

    //     // if the nb of headers is already above the limit and we encounter another one, we generate an error
    //     // and we reset the counters
    //     if (nbHeadings >= max_nb_headings) {
    //         onError({
    //             lineNumber: lineIndex,
    //         });
    //     }
    // });
    // };

    const tooFewImagesPerHeadings = (params, onError) => {
        // params.parsers.markdownit.tokens.filter((token) => {
        //   console.log(token.type);
        //   console.log(token.line);
        //   // return token.type === "blockquote_open";
        //   return token.type === "inline";
        // }).forEach(function forToken(blockquote) {
        //   console.log(blockquote);
        //   var lines = blockquote.map[1] - blockquote.map[0];
        //   onError({
        //     "lineNumber": blockquote.lineNumber,
        //     "detail": "Blockquote spans " + lines + " line(s).",
        //     "context": blockquote.line.substr(0, 7)
        //   });
        // });
        params.parsers.markdownit.tokens.forEach((blockquote) => {
          // console.log(blockquote);

          if(blockquote.type == "heading_open"){
            nbHeadings = nbHeadings + 1;
          }

          if(blockquote.type == "image"){
            //imageFound = true;
            imageFound = true;
          }

          console.log("nbHeadings = " + nbHeadings + ", Image Found  = " + imageFound);

          if(!imageFound && nbHeadings > max_nb_headings){
            onError({
              "lineNumber": blockquote.lineNumber,
              "detail": "Blockquote spans " + lines + " line(s).",
              "context": blockquote.line.substr(0, 7)
            });
          }

          if(blockquote.children !== null){
            blockquote.children.forEach((bqitem) => {
              console.log("blockquote item type = " + bqitem.type);
              console.log("blockquote item content = " + bqitem.content);
              if(bqitem.type == "heading"){
                nbHeadings = nbHeadings + 1;
              }
    
              if(bqitem.type == "image"){
                //imageFound = true;
                nbHeadings = 0;
              }

              console.log("nbHeadings = " + nbHeadings + ", Image Found  = " + imageFound);

              if(!imageFound && nbHeadings > max_nb_headings){
                onError({
                  "lineNumber": bqitem.lineNumber,
                  "detail": "Blockquote spans " + lines + " line(s).",
                  "context": bqitem.line.substr(0, 7)
                });
              }
            });
          }

          // var lines = blockquote.map[1] - blockquote.map[0];
          // onError({
          //   "lineNumber": blockquote.lineNumber,
          //   "detail": "Blockquote spans " + lines + " line(s).",
          //   "context": blockquote.line.substr(0, 7)
          // });
        });
      }
    
    module.exports = {
    names: ["CMD002", "too-few-images-per-heading"],
    description: "You should have an image every " + max_nb_headings + " headings",
    tags: ["test", "image_in_post"],
    function: tooFewImagesPerHeadings,
    };
