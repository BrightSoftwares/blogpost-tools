const {
    forEachLine,
    getLineMetadata,
    inlineCommentStartRe,
    } = require("markdownlint-rule-helpers");
    
    const start_highlight = /{% highlight \w+ %}/;
    const end_highlight = "{% endhighlight %}";
    
    const noRenderedComments = (params, onError) => {
    let insideHighlightBlock = false;
    forEachLine(getLineMetadata(params), (line, lineIndex) => {
        if (line && start_highlight.test(line)) {
        insideHighlightBlock = true;
        }
        if (line && line == end_highlight) {
        insideHighlightBlock = false;
        }
        const isComment = line.startsWith("<!--"); // inlineCommentStartRe.test(line);
        //console.log("This is a comment ? " + isComment + ", insideHighlightBlock " + insideHighlightBlock  + ", line =" + line);
        //console.log("");
        if (insideHighlightBlock && isComment) {
            onError({
                lineNumber: lineIndex,
            });
        }
    });
    };
    
    module.exports = {
    names: ["CMD001", "no-rendered-comments"],
    description: "No markdown comments should be inside code blocks",
    tags: ["test"],
    function: noRenderedComments,
    };