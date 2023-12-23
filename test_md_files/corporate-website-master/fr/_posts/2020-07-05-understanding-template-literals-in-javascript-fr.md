---
layout: flexstart-blog-single
title: "Understanding Template Literals in JavaScript"
author: full
lang: fr
ref: javascripttemplate_1240
categories: [javascript]
description: "The 2015 edition of the ECMAScript specification (ES6) added template literals to the JavaScript language. Template literals are a new form of making strings in JavaScript that add a lot of powerful new capabilities, such as creating multi-line strings more easily and using placeholders to embed expressions in a string. In addition, an advanced feature called tagged template literals allows you to perform operations on the expressions within a string. All of these capabilities increase your options for string manipulation as a developer, letting you generate dynamic strings that could be used for URLs or functions that customize HTML elements."
image: "https://sergio.afanou.com/assets/images/image-midres-36.jpg"
---

<p><em>The author selected the <a href="https://www.brightfunds.org/funds/write-for-donations-covid-19-relief-fund">COVID-19 Relief Fund</a> to receive a donation as part of the <a href="https://do.co/w4do-cta">Write for DOnations</a> program.</em></p>

<h3 id="introduction">Introduction</h3>

<p>The <a href="http://www.ecma-international.org/ecma-262/6.0/">2015 edition of the ECMAScript specification (ES6)</a> added <em>template literals</em> to the JavaScript language. Template literals are a new form of making <a href="https://www.digitalocean.com/community/tutorials/how-to-work-with-strings-in-javascript">strings in JavaScript</a> that add a lot of powerful new capabilities, such as creating multi-line strings more easily and using placeholders to embed expressions in a string. In addition, an advanced feature called <em>tagged template literals</em> allows you to perform operations on the expressions within a string. All of these capabilities increase your options for string manipulation as a developer, letting you generate dynamic strings that could be used for <a href="https://developer.mozilla.org/en-US/docs/Learn/Common_questions/What_is_a_URL">URLs</a> or functions that customize <a href="https://developer.mozilla.org/en-US/docs/Web/HTML">HTML elements</a>.</p>

<p>In this article, you will go over the differences between single/double-quoted strings and template literals, running through the various ways to declare strings of different shape, including multi-line strings and dynamic strings that change depending on the value of a variable or expression. You will then learn about tagged templates and see some real-world examples of projects using them.</p>

<h2 id="declaring-strings">Declaring Strings</h2>

<p>This section will review how to declare strings with single quotes and double quotes, and will then show you how to do the same with template literals.</p>

<p>In JavaScript, a string can be written with single quotes (<code>' '</code>):</p>
<pre class="code-pre "><code class="code-highlight language-js">const single = 'Every day is a good day when you paint.'
</code></pre>
<p>A string can also be written with double quotes (<code>" "</code>):</p>
<pre class="code-pre "><code class="code-highlight language-js">const double = "Be so very light. Be a gentle whisper."
</code></pre>
<p>There is no major difference in JavaScript between single- or double-quoted strings, unlike other languages that might allow <em>interpolation</em> in one type of string but not the other. In this context, interpolation refers to the evaluation of a placeholder as a dynamic part of a string.</p>

<p>The use of single- or double-quoted strings mostly comes down to personal preference and convention, but used in conjunction, each type of string only needs to <a href="https://www.digitalocean.com/community/tutorials/how-to-work-with-strings-in-javascript#escaping-quotes-and-apostrophes-in-strings">escape</a> its own type of quote:</p>
<pre class="code-pre "><code class="code-highlight language-js">// Escaping a single quote in a single-quoted string
const single = '"We don\'t make mistakes. We just have happy accidents." - Bob Ross'

// Escaping a double quote in a double-quoted string
const double = "\"We don't make mistakes. We just have happy accidents.\" - Bob Ross"

console.log(single);
console.log(double);
</code></pre>

<p>The result of the <code>log()</code> method here will print the same two strings to the <a href="https://www.digitalocean.com/community/tutorials/how-to-use-the-javascript-developer-console">console</a>:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>"We don't make mistakes. We just have happy accidents." - Bob Ross
"We don't make mistakes. We just have happy accidents." - Bob Ross
</code></pre>
<p>Template literals, on the other hand, are written by surrounding the string with the backtick character, or grave accent (<code>`</code>):</p>
<pre class="code-pre "><code class="code-highlight language-js">const template = `Find freedom on this canvas.`
</code></pre>
<p>They do not need to escape single or double quotes:</p>
<pre class="code-pre "><code class="code-highlight language-js">const template = `"We don't make mistakes. We just have happy accidents." - Bob Ross`
</code></pre>
<p>However, they do still need to escape backticks:</p>
<pre class="code-pre "><code class="code-highlight language-js">const template = `Template literals use the \` character.`
</code></pre>
<p>Template literals can do everything that regular strings can, so you could possibly replace all strings in your project with them and have the same functionality. However, the most common convention in codebases is to only use template literals when using the additional capabilities of template literals, and consistently using the single or double quotes for all other simple strings. Following this standard will make your code easier to read if examined by another developer.</p>

<p>Now that you&rsquo;ve seen how to declare strings with single quotes, double quotes, and backticks, you can move on to the first advantage of template literals: writing multi-line strings.</p>

<h2 id="multi-line-strings">Multi-line Strings</h2>

<p>In this section, you will first run through the way strings with multiple lines were declared before ES6, then see how template literals make this easier.</p>

<p>Originally, if you wanted to write a string that spans multiple lines in your text editor, you would use the <a href="https://www.digitalocean.com/community/tutorials/how-to-work-with-strings-in-javascript#string-concatenation">concatenation operator</a>. However, this was not always a straight-forward process. The following string concatenation seemed to run over multiple lines:</p>
<pre class="code-pre "><code class="code-highlight language-js">const address = 
  'Homer J. Simpson' + 
  '742 Evergreen Terrace' + 
  'Springfield'
</code></pre>
<p>This might allow you to break up the string into smaller lines and include it over multiple lines in the text editor, but it has no effect on the output of the string. In this case, the strings will all be on one line and not separated by newlines or spaces. If you logged <code>address</code> to the console, you would get the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Homer J. Simpson742 Evergreen TerraceSpringfield
</code></pre>
<p>You can use the backslash character (<code>\</code>) to continue the string onto multiple lines:</p>
<pre class="code-pre "><code class="code-highlight language-js">const address =
  'Homer J. Simpson\
  742 Evergreen Terrace\
  Springfield'
</code></pre>
<p>This will retain any indentation as whitespace, but the string will still be on one line in the output:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Homer J. Simpson  742 Evergreen Terrace  Springfield
</code></pre>
<p>Using the newline character (<code>\n</code>), you can create a true multi-line string:</p>
<pre class="code-pre "><code class="code-highlight language-js">const address = 
  'Homer J. Simpson\n' + 
  '742 Evergreen Terrace\n' + 
  'Springfield'
</code></pre>
<p>When logged to the console, this will display the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Homer J. Simpson
742 Evergreen Terrace
Springfield
</code></pre>
<p>Using newline characters to designate multi-line strings can be counterintuitive, however. In contrast, creating a multi-line string with template literals can be much more straight-forward. There is no need to concatenate, use newline characters, or use backslashes. Just pressing <code>ENTER</code> and writing the string across multiple lines works by default:</p>
<pre class="code-pre "><code class="code-highlight language-js">const address = `Homer J. Simpson
742 Evergreen Terrace
Springfield`
</code></pre>
<p>The output of logging this to the console is the same as the input:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Homer J. Simpson
742 Evergreen Terrace
Springfield
</code></pre>
<p>Any indentation will be preserved, so it&rsquo;s important not to indent any additional lines in the string if that is not desired. For example, consider the following:</p>
<pre class="code-pre "><code class="code-highlight language-js">const address = `Homer J. Simpson
                 742 Evergreen Terrace
                 Springfield`
</code></pre>
<p>Although this style of writing the line might make the code more human readable, the output will not be:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Homer J. Simpson
                 742 Evergreen Terrace
                 Springfield
</code></pre>
<p>With multi-line strings now covered, the next section will deal with how expressions are interpolated into their values with the different string declarations.</p>

<h2 id="expression-interpolation">Expression Interpolation</h2>

<p>In strings before ES6, concatenation was used to create a dynamic string with variables or expressions:</p>
<pre class="code-pre "><code class="code-highlight language-js">const method = 'concatenation'
const dynamicString = 'This string is using ' + method + '.'
</code></pre>
<p>When logged to the console, this will yield the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>This string is using concatenation.
</code></pre>
<p>With template literals, an expression can be embedded in a <em>placeholder</em>. A placeholder is represented by <code>${}</code>, with anything within the curly brackets treated as JavaScript and anything outside the brackets treated as a string:</p>
<pre class="code-pre "><code class="code-highlight language-js">const method = 'interpolation'
const dynamicString = `This string is using ${method}.`
</code></pre>
<p>When <code>dynamicString</code> is logged to the console, the console will show the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>This string is using interpolation.
</code></pre>
<p>One common example of embedding values in a string might be for creating dynamic URLs. With concatenation, this can be cumbersome. For example, the following declares a <a href="https://www.digitalocean.com/community/tutorials/how-to-define-functions-in-javascript">function</a> to generate an <a href="https://tools.ietf.org/html/rfc6749">OAuth</a> access string:</p>
<pre class="code-pre "><code class="code-highlight language-js">function createOAuthString(host, clientId, scope) {
  return host + '/login/oauth/authorize?client_id=' + clientId + '&amp;scope=' + scope
}

createOAuthString('https://github.com', 'abc123', 'repo,user')
</code></pre>

<p>Logging this function will yield the following URL to the console:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>https://github.com/login/oauth/authorize?client_id=abc123&amp;scope=repo,user
</code></pre>
<p>Using string interpolation, you no longer have to keep track of opening and closing strings and concatenation operator placement. Here is the same example with template literals:</p>
<pre class="code-pre "><code class="code-highlight language-js">function createOAuthString(host, clientId, scope) {
  return `${host}/login/oauth/authorize?client_id=${clientId}&amp;scope=${scope}`
}

createOAuthString('https://github.com', 'abc123', 'repo,user')
</code></pre>

<p>This will have the same output as the concatenation example:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>https://github.com/login/oauth/authorize?client_id=abc123&amp;scope=repo,user
</code></pre>
<p>You can also use the <a href="https://www.digitalocean.com/community/tutorials/how-to-index-split-and-manipulate-strings-in-javascript#trimming-whitespace"><code>trim()</code> method</a> on a template literal to remove any whitespace at the beginning or end of the string. For example, the following uses an <a href="https://www.digitalocean.com/community/tutorials/how-to-define-functions-in-javascript#arrow-functions">arrow function</a> to create an HTML <a href="https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li"><code>&lt;li&gt;</code> element</a> with a customized link:</p>
<pre class="code-pre "><code class="code-highlight language-js">const menuItem = (url, link) =&gt;
  `
&lt;li&gt;
  &lt;a href="${url}"&gt;${link}&lt;/a&gt;
&lt;/li&gt;
`.trim()

menuItem('https://google.com', 'Google')
</code></pre>

<p>The result will be trimmed of all the whitespace, ensuring that the element will be rendered correctly:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>&lt;li&gt;
  &lt;a href="https://google.com"&gt;Google&lt;/a&gt;
&lt;/li&gt;
</code></pre>
<p>Entire expressions can be interpolated, not just variables, such as in this example of the sum of two numbers:</p>
<pre class="code-pre "><code class="code-highlight language-js">const sum = (x, y) =&gt; x + y
const x = 5
const y = 100
const string = `The sum of ${x} and ${y} is ${sum(x, y)}.`

console.log(string)
</code></pre>

<p>This code defines the <code>sum</code> function and the variables <code>x</code> and <code>y</code>, then uses both the function and the variables in a string. The logged result will show the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>The sum of 5 and 100 is 105.
</code></pre>
<p>This can be particularly useful with <a href="https://www.digitalocean.com/community/tutorials/how-to-write-conditional-statements-in-javascript#ternary-operator">ternary operators</a>, which allow conditionals within a string:</p>
<pre class="code-pre "><code class="code-highlight language-js">const age = 19
const message = `You can ${age &lt; 21 ? 'not' : ''} view this page`
console.log(message)
</code></pre>
<p>The logged message here will change depnding on whether the value of <code>age</code> is over or under <code>21</code>. Since it is <code>19</code> in this example, the following output will be logged:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>You can not view this page
</code></pre>
<p>Now you have an idea of how template literals can be useful when used to interpolate expressions. The next section will take this a step further by examining tagged template literals to work with the expressions passed into placeholders.</p>

<h2 id="tagged-template-literals">Tagged Template Literals</h2>

<p>An advanced feature of template literals is the use of <em>tagged template literals</em>, sometimes referred to as <em>template tags</em>. A tagged template starts with a <em>tag function</em> that parses a template literal, allowing you more control over manipulating and returning a dynamic string.</p>

<p>In this example, you&rsquo;ll create a <code>tag</code> function to use as the function operating on a tagged template. The string literals are the first parameter of the function, named <code>strings</code> here, and any expressions interpolated into the string are packed into the second parameter using <a href="https://www.digitalocean.com/community/tutorials/understanding-destructuring-rest-parameters-and-spread-syntax-in-javascript">rest parameters</a>. You can console out the parameter to see what they will contain:</p>
<pre class="code-pre "><code class="code-highlight language-js">function tag(strings, ...expressions) {
  console.log(strings)
  console.log(expressions)
}
</code></pre>
<p>Use the <code>tag</code> function as the tagged template function and parse the string as follows:</p>
<pre class="code-pre "><code class="code-highlight language-js">const string = tag`This is a string with ${true} and ${false} and ${100} interpolated inside.`
</code></pre>
<p>Since you&rsquo;re console logging <code>strings</code> and <code>expressions</code>, this will be the output:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>(4) ["This is a string with ", " and ", " and ", " interpolated inside."
(3) [true, false, 100]
</code></pre>
<p>The first parameter, <code>strings</code>, is an <a href="https://www.digitalocean.com/community/tutorials/understanding-arrays-in-javascript">array</a> containing all the string literals:</p>

<ul>
<li><code>"This is a string with "</code></li>
<li><code>" and "</code></li>
<li><code>" and "</code></li>
<li><code>" interpolated inside."</code></li>
</ul>

<p>There is also a <code>raw</code> property available on this argument at <code>strings.raw</code>, which contains the strings without any escape sequences being processed. For example, <code>/n</code> would just be the character <code>/n</code> and not be escaped into a newline.</p>

<p>The second parameter, <code>...expressions</code>, is a rest parameter array consisting of all the expressions:</p>

<ul>
<li><code>true</code></li>
<li><code>false</code></li>
<li><code>100</code></li>
</ul>

<p>The string literals and expressions are passed as parameters to the tagged template function <code>tag</code>. Note that the tagged template does not need to return a string; it can operate on those values and return any type of value. For example, we can have the function ignore everything and return <code>null</code>, as in this <code>returnsNull</code> function:</p>
<pre class="code-pre "><code class="code-highlight language-js">function returnsNull(strings, ...expressions) {
  return null
}

const string = returnsNull`Does this work?`
console.log(string)
</code></pre>

<p>Logging the <code>string</code> variable will return:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>null
</code></pre>
<p>An example of an action that can be performed in tagged templates is applying some change to both sides of each expression, such as if you wanted to wrap each expression in an HTML tag. Create a <code>bold</code> function that will add <code>&lt;strong&gt;</code> and <code>&lt;/strong&gt;</code> to each expression:</p>
<pre class="code-pre "><code class="code-highlight language-js">function bold(strings, ...expressions) {
  let finalString = ''

// Loop through all expressions
expressions.forEach((value, i) =&gt; {
finalString += `${strings[i]}&lt;strong&gt;${value}&lt;/strong&gt;`
})

// Add the last string literal
finalString += strings[strings.length - 1]

return finalString
}

const string = bold`This is a string with ${true} and ${false} and ${100} interpolated inside.`

console.log(string)
</code></pre>

<p>This code uses the <a href="https://www.digitalocean.com/community/tutorials/how-to-use-array-methods-in-javascript-iteration-methods#foreach()"><code>forEach</code> method</a> to loop over the <code>expressions</code> array and add the bolding element:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>This is a string with &lt;strong&gt;true&lt;/strong&gt; and &lt;strong&gt;false&lt;/strong&gt; and &lt;strong&gt;100&lt;/strong&gt; interpolated inside.
</code></pre>
<p>There are a few examples of tagged template literals in popular JavaScript libraries. The <a href="https://github.com/apollographql/graphql-tag"><code>graphql-tag</code></a> library uses the <code>gql</code> tagged template to parse <a href="https://graphql.org/">GraphQL</a> query strings into the abstract syntax tree (AST) that GraphQL understands:</p>
<pre class="code-pre "><code class="code-highlight language-js">import gql from 'graphql-tag'

// A query to retrieve the first and last name from user 5
const query = gql` { user(id: 5) { firstName lastName } }`
</code></pre>

<p>Another library that uses tagged template functions is <a href="https://github.com/styled-components/styled-components"><code>styled-components</code></a>, which allows you to create new <a href="https://www.digitalocean.com/community/tutorials/how-to-create-custom-components-in-react">React components</a> from regular <a href="https://www.digitalocean.com/community/tutorials/introduction-to-the-dom">DOM</a> elements and apply additional <a href="https://developer.mozilla.org/en-US/docs/Web/CSS">CSS styles</a> to them:</p>
<pre class="code-pre "><code class="code-highlight language-js">import styled from 'styled-components'

const Button = styled.button` color: magenta;`

// &lt;Button&gt; can now be used as a custom component
</code></pre>

<p>You can also use the built-in <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/raw"><code>String.raw</code></a> method on tagged template literals to prevent any escape sequences from being processed:</p>
<pre class="code-pre "><code class="code-highlight language-js">const rawString = String.raw`I want to write /n without it being escaped.`
console.log(rawString)
</code></pre>
<p>This will log the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>I want to write /n without it being escaped.
</code></pre>
<h2 id="conclusion">Conclusion</h2>

<p>In this article, you reviewed single- and double-quoted string literals and you learned about template literals and tagged template literals. Template literals make a lot of common string tasks simpler by interpolating expressions in strings and creating multi-line strings without any concatenation or escaping. Template tags are also a useful advanced feature of template literals that many popular libraries have used, such as GraphQL and <code>styled-components</code>.</p>

<p>To learn more about strings in JavaScript, read <a href="https://www.digitalocean.com/community/tutorials/how-to-work-with-strings-in-javascript">How To Work with Strings in JavaScript</a> and <a href="https://www.digitalocean.com/community/tutorials/how-to-index-split-and-manipulate-strings-in-javascript">How To Index, Split, and Manipulate Strings in JavaScript</a>.</p>
