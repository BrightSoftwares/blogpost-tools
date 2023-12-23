---
layout: flexstart-blog-single
title: "How To Manage State on React Class Components"
author: full
lang: fr
ref: reactclass_components_1238
categories: [javascript]
description: "In React, state refers to a structure that keeps track of how data changes over time in your application. Managing state is a crucial skill in React because it allows you to make interactive components and dynamic web applications. State is used for everything from tracking form inputs to capturing dynamic data from an API. In this tutorial, you’ll run through an example of managing state on class-based components."
image: "https://sergio.afanou.com/assets/images/image-midres-43.jpg"
---

<p><em>The author selected <a href="https://creativecommons.org/">Creative Commons</a> to receive a donation as part of the <a href="https://do.co/w4do-cta">Write for DOnations</a> program.</em></p>

<h3 id="introduction">Introduction</h3>

<p>In <a href="https://reactjs.org/">React</a>, <em>state</em> refers to a structure that keeps track of how data changes over time in your application. Managing state is a crucial skill in React because it allows you to make interactive components and dynamic web applications. State is used for everything from tracking form inputs to capturing dynamic data from an API. In this tutorial, you&rsquo;ll run through an example of managing <a href="https://reactjs.org/docs/state-and-lifecycle.html">state</a> on class-based <a href="https://www.digitalocean.com/community/tutorials/how-to-create-custom-components-in-react">components</a>.</p>

<p>As of the writing of this tutorial, the official <a href="https://reactjs.org/docs/hooks-faq.html#should-i-use-hooks-classes-or-a-mix-of-both">React documentation</a> encourages developers to adopt <a href="https://reactjs.org/docs/hooks-state.html">React Hooks</a> to manage state with <a href="https://www.digitalocean.com/community/tutorials/how-to-create-custom-components-in-react#step-4-%E2%80%94-building-a-functional-component">functional components</a> when writing new code, rather than using <a href="https://www.digitalocean.com/community/tutorials/how-to-create-custom-components-in-react#step-2-%E2%80%94-creating-an-independent-component-with-react-classes">class-based components</a>. Although the use of React Hooks is considered a more modern practice, it&rsquo;s important to understand how to manage state on class-based components as well. Learning the concepts behind state management will help you navigate and troubleshoot class-based state management in existing code bases and help you decide when class-based state management is more appropriate. There&rsquo;s also a class-based method called <a href="https://reactjs.org/docs/error-boundaries.html"><code>componentDidCatch</code></a> that is not available in Hooks and will require setting state using class methods.</p>

<p>This tutorial will first show you how to set state using a static value, which is useful for cases where the next state does not depend on the first state, such as setting data from an API that overrides old values. Then it will run through how to set a state as the current state, which is useful when the next state depends on the current state, such as toggling a value. To explore these different ways of setting state, you&rsquo;ll create a product page component that you&rsquo;ll update by adding purchases from a list of options.</p>

<h3 id="prerequisites">Prerequisites</h3>

<ul>
<li><p>You will need a development environment running <a href="https://nodejs.org/en/about/">Node.js</a>; this tutorial was tested on Node.js version 10.20.1 and npm version 6.14.4. To install this on macOS or Ubuntu 18.04, follow the steps in <a href="https://www.digitalocean.com/community/tutorials/how-to-install-node-js-and-create-a-local-development-environment-on-macos">How to Install Node.js and Create a Local Development Environment on macOS</a> or the <strong>Installing Using a PPA</strong> section of <a href="https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-18-04">How To Install Node.js on Ubuntu 18.04</a>.</p></li>
<li><p>In this tutorial, you will create apps with <a href="https://github.com/facebook/create-react-app">Create React App</a>. You can find instructions for installing an application with Create React App at <a href="https://www.digitalocean.com/community/tutorials/how-to-set-up-a-react-project-with-create-react-app">How To Set Up a React Project with Create React App</a>.</p></li>
<li><p>You will also need a basic knowledge of JavaScript, which you can find in <a href="https://www.digitalocean.com/community/tutorial_series/how-to-code-in-javascript">How To Code in JavaScript</a>, along with a basic knowledge of HTML and CSS. A good resource for HTML and CSS is the <a href="https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML">Mozilla Developer Network</a>.</p></li>
</ul>

<h2 id="step-1-—-creating-an-empty-project">Step 1 — Creating an Empty Project</h2>

<p>In this step, you&rsquo;ll create a new project using <a href="https://github.com/facebook/create-react-app">Create React App</a>. Then you will delete the sample project and related files that are installed when you bootstrap the project. Finally, you will create a simple file structure to organize your components. This will give you a solid basis on which to build this tutorial&rsquo;s sample application for managing state on class-based components.</p>

<p>To start, make a new project. In your terminal, run the following script to install a fresh project using <code>create-react-app</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">npx create-react-app <span class="highlight">state-class-tutorial</span>
</li></ul></code></pre>
<p>After the project is finished, change into the directory:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">cd <span class="highlight">state-class-tutorial</span>
</li></ul></code></pre>
<p>In a new terminal tab or window, start the project using the <a href="https://www.digitalocean.com/community/tutorials/how-to-set-up-a-react-project-with-create-react-app#step-3-%E2%80%94-starting-the-server">Create React App start script</a>. The browser will auto-refresh on changes, so leave this script running while you work:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">npm start
</li></ul></code></pre>
<p>You will get a running local server. If the project did not open in a browser window, you can open it with <a href="http://localhost:3000/"><code>http://localhost:3000/</code></a>. If you are running this from a remote server, the address will be <code>http://<span class="highlight">your_domain</span>:3000</code>.</p>

<p>Your browser will load with a simple React application included as part of Create React App:</p>

<p><img src="https://assets.digitalocean.com/articles/67105/react-template.png" alt="React template project"></p>

<p>You will be building a completely new set of custom components, so you&rsquo;ll need to start by clearing out some boilerplate code so that you can have an empty project.</p>

<p>To start, open <code>src/App.js</code> in a text editor. This is the root component that is injected into the page. All components will start from here. You can find more information about <code>App.js</code> at <a href="https://www.digitalocean.com/community/tutorials/how-to-set-up-a-react-project-with-create-react-app#step-5-%E2%80%94-modifying-the-heading-tag-and-styling">How To Set Up a React Project with Create React App</a>.</p>

<p>Open <code>src/App.js</code> with the following command:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/App.js
</li></ul></code></pre>
<p>You will see a file like this:</p>
<div class="code-label " title="state-class-tutorial/src/App.js">state-class-tutorial/src/App.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
return (
&lt;div className="App"&gt;
&lt;header className="App-header"&gt;
&lt;img src={logo} className="App-logo" alt="logo" /&gt;
&lt;p&gt;
Edit &lt;code&gt;src/App.js&lt;/code&gt; and save to reload.
&lt;/p&gt;
&lt;a
className="App-link"
href="https://reactjs.org"
target="\_blank"
rel="noopener noreferrer"
&gt;
Learn React
&lt;/a&gt;
&lt;/header&gt;
&lt;/div&gt;
);
}

export default App;
</code></pre>

<p>Delete the line <code>import logo from './logo.svg';</code>. Then replace everything in the <code>return</code> statement to return a set of empty tags: <code>&lt;&gt;&lt;/&gt;</code>. This will give you a valid page that returns nothing. The final code will look like this:</p>
<div class="code-label " title="state-class-tutorial/src/App.js">state-class-tutorial/src/App.js</div><pre class="code-pre "><code class="code-highlight language-javascript">
import React from 'react';
import './App.css';

function App() {
return <span class="highlight">&lt;&gt;&lt;/&gt;;</span>
}

export default App;
</code></pre>

<p>Save and exit the text editor.</p>

<p>Finally, delete the logo. You won&rsquo;t be using it in your application and you should remove unused files as you work. It will save you from confusion in the long run.</p>

<p>In the terminal window type the following command:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">rm src/logo.svg
</li></ul></code></pre>
<p>If you look at your browser, you will see a blank screen.</p>

<p><img src="https://assets.digitalocean.com/articles/67105/blank-chrome.png" alt="blank screen in chrome"></p>

<p>Now that you have cleared out the sample Create React App project, create a simple file structure. This will help you keep your components isolated and independent.</p>

<p>Create a directory called <code>components</code> in the <code>src</code> directory. This will hold all of your custom components.</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">mkdir src/components
</li></ul></code></pre>
<p>Each component will have its own directory to store the component file along with the styles, images, and tests.</p>

<p>Create a directory for <code>App</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">mkdir src/components/App
</li></ul></code></pre>
<p>Move all of the <code>App</code> files into that directory. Use the wildcard, <code>*</code>, to select any files that start with <code>App.</code> regardless of file extension. Then use the <code>mv</code> command to put them into the new directory:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">mv src/App.* src/components/App
</li></ul></code></pre>
<p>Next, update the relative import path in <code>index.js</code>, which is the root component that bootstraps the whole process:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/index.js
</li></ul></code></pre>
<p>The import statement needs to point to the <code>App.js</code> file in the <code>App</code> directory, so make the following highlighted change:</p>
<div class="code-label " title="state-class-tutorial/src/index.js">state-class-tutorial/src/index.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from '.<span class="highlight">/components/App</span>/App';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
&lt;React.StrictMode&gt;
&lt;App /&gt;
&lt;/React.StrictMode&gt;,
document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
</code></pre>

<p>Save and exit the file.</p>

<p>Now that the project is set up, you can create your first component.</p>

<h2 id="step-2-—-using-state-in-a-component">Step 2 — Using State in a Component</h2>

<p>In this step, you&rsquo;ll set the initial state of a component on its class and reference the state to display a value. You&rsquo;ll then make a product page with a shopping cart that displays the total items in the cart using the state value. By the end of the step, you&rsquo;ll know the different ways to hold a value and when you should use state rather than a prop or a static value.</p>

<h3 id="building-the-components">Building the Components</h3>

<p>Start by creating a directory for <code>Product</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">mkdir src/components/Product
</li></ul></code></pre>
<p>Next, open up <code>Product.js</code> in that directory:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/components/Product/Product.js
</li></ul></code></pre>
<p>Start by creating a component with no state. The component will have two parts: The cart, which has the number of items and the total price, and the product, which has a button to add and remove an item. For now, the buttons will have no actions.</p>

<p>Add the following code to <code>Product.js</code>:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

export default class Product extends Component {
render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: 0 total items.
&lt;/div&gt;
&lt;div&gt;Total: 0&lt;/div&gt;

        &lt;div className="product"&gt;&lt;span role="img" aria-label="ice cream"&gt;🍦&lt;/span&gt;&lt;/div&gt;
        &lt;button&gt;Add&lt;/button&gt; &lt;button&gt;Remove&lt;/button&gt;
      &lt;/div&gt;
    )

}
}
</code></pre>

<p>You have also included a couple of <code>div</code> elements that have <a href="https://www.digitalocean.com/community/tutorials/how-to-create-react-elements-with-jsx">JSX</a> class names so you can add some basic styling.</p>

<p>Save and close the file, then open <code>Product.css</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/components/Product/Product.css
</li></ul></code></pre>
<p>Give some light styling to increase the <code>font-size</code> for the text and the emoji:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.css">state-class-tutorial/src/components/Product/Product.css</div><pre class="code-pre "><code class="code-highlight language-css">.product span {
    font-size: 100px;
}

.wrapper {
padding: 20px;
font-size: 20px;
}

.wrapper button {
font-size: 20px;
background: none;
}
</code></pre>

<p>The emoji will need a much larger font size than the text, since it&rsquo;s acting as the product image in this example. In addition, you are removing the default gradient background on buttons by setting the <code>background</code> to <code>none</code>. </p>

<p>Save and close the file.</p>

<p>Now, render the <code>Product</code> component in the <code>App</code> component so you can see the results in the browser. Open <code>App.js</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/components/App/App.js
</li></ul></code></pre>
<p>Import the component and render it. You can also delete the CSS import since you won&rsquo;t be using it in this tutorial:</p>
<div class="code-label " title="state-class-tutorial/src/components/App/App.js">state-class-tutorial/src/components/App/App.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React from 'react';
<span class="highlight">import Product from '../Product/Product';</span>

function App() {
return &lt;<span class="highlight">Product </span>/&gt;
}

export default App;
</code></pre>

<p>Save and close the file. When you do, the browser will refresh and you&rsquo;ll see the <code>Product</code> component.</p>

<p><img src="https://assets.digitalocean.com/articles/67228/product-page.png" alt="Product Page"></p>

<h3 id="setting-the-initial-state-on-a-class-component">Setting the Initial State on a Class Component</h3>

<p>There are two values in your component values that are going to change in your display: total number of items and total cost. Instead of hard coding them, in this step you&rsquo;ll move them into an <a href="https://www.digitalocean.com/community/tutorials/understanding-objects-in-javascript">object</a> called <code>state</code>.</p>

<p>The <code>state</code> of a React class is a special property that controls the rendering of a page. When you change the state, React knows that the component is out-of-date and will automatically re-render. When a component re-renders, it modifies the rendered output to include the most up-to-date information in <code>state</code>. In this example, the component will re-render whenever you add a product to the cart or remove it from the cart. You can add other properties to a React class, but they won&rsquo;t have the same ability to trigger re-rendering.</p>

<p>Open <code>Product.js</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/components/Product/Product.js
</li></ul></code></pre>
<p>Add a property called <code>state</code> to the <code>Product</code> class. Then add two values to the <code>state</code> object: <code>cart</code> and <code>total</code>. The <code>cart</code> will be an <a href="https://www.digitalocean.com/community/tutorials/understanding-arrays-in-javascript">array</a>, since it may eventually hold many items. The <code>total</code> will be a number. After assigning these, replace references to the values with <code>this.state.<span class="highlight">property</span></code>:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">
import React, { Component } from 'react';
import './Product.css';

export default class Product extends Component {

<span class="highlight">state = {</span>
<span class="highlight">cart: [],</span>
<span class="highlight">total: 0</span>
<span class="highlight">}</span>

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: <span class="highlight">{this.state.cart.length}</span> total items.
&lt;/div&gt;
&lt;div&gt;Total <span class="highlight">{this.state.total}</span>&lt;/div&gt;

        &lt;div className="product"&gt;&lt;span role="img" aria-label="ice cream"&gt;🍦&lt;/span&gt;&lt;/div&gt;
        &lt;button&gt;Add&lt;/button&gt; &lt;button&gt;Remove&lt;/button&gt;
      &lt;/div&gt;
    )

}
}
</code></pre>

<p>Notice that in both cases, since you are referencing JavaScript inside of your JSX, you need to wrap the code in curly braces. You are also displaying the <code>length</code> of the <code>cart</code> array to get a count of the number of items in the array.</p>

<p>Save the file. When you do, the browser will refresh and you&rsquo;ll see the same page as before.</p>

<p><img src="https://assets.digitalocean.com/articles/67228/product-page.png" alt="Product Page"></p>

<p>The <code>state</code> property is a standard class property, which means that it is accessible in other methods, not just the <code>render</code> method.</p>

<p>Next, instead of displaying the price as a static value, convert it to a string using the <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/toLocaleString"><code>toLocaleString</code></a> method, which will convert the number to a string that matches the way numbers are displayed in the browser&rsquo;s region.</p>

<p>Create a method called <code>getTotal()</code> that takes the <code>state</code> and converts it to a localized string using an array of <code>currencyOptions</code>. Then, replace the reference to <code>state</code> in the JSX with a method call:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

export default class Product extends Component {

state = {
cart: [],
total: 0
}

<span class="highlight">currencyOptions = {</span>
<span class="highlight">minimumFractionDigits: 2,</span>
<span class="highlight">maximumFractionDigits: 2,</span>
<span class="highlight">}</span>

<span class="highlight">getTotal = () =&gt; {</span>
<span class="highlight">return this.state.total.toLocaleString(undefined, this.currencyOptions)</span>
<span class="highlight">}</span>

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: {this.state.cart.length} total items.
&lt;/div&gt;
&lt;div&gt;Total {this.<span class="highlight">getTotal()</span>}&lt;/div&gt;

        &lt;div className="product"&gt;&lt;span role="img" aria-label="ice cream"&gt;🍦&lt;/span&gt;&lt;/div&gt;
        &lt;button&gt;Add&lt;/button&gt; &lt;button&gt;Remove&lt;/button&gt;
      &lt;/div&gt;
    )

}
}
</code></pre>

<p>Since <code>total</code> is a price for goods, you are passing <code>currencyOptions</code> that set the maximum and minimum decimal places for your <code>total</code> to two. Note that this is set as a separate property. Often, beginner React developers will put information like this in the <code>state</code> object, but it is best to only add information to <code>state</code> that you expect to change. This way, the information in <code>state</code> will be easier to keep strack of as your application scales.</p>

<p>Another important change you made was to create the <code>getTotal()</code> method by assigning an <a href="https://www.digitalocean.com/community/tutorials/getting-started-with-es6-arrow-functions-in-javascript">arrow function</a> to a class property. Without using the arrow function, this method would create a new <a href="https://www.digitalocean.com/community/conceptual_articles/understanding-this-bind-call-and-apply-in-javascript"><code>this</code> binding</a>, which would interfere with the current <code>this</code> binding and introduce a bug into our code. You&rsquo;ll see more on this in the next step.</p>

<p>Save the file. When you do, the page will refresh and you&rsquo;ll see the value converted to a decimal.</p>

<p><img src="https://assets.digitalocean.com/articles/67228/price-converted-decimal.png" alt="Price converted to decimal"></p>

<p>You&rsquo;ve now added state to a component and referenced it in your class. You also accessed values in the <code>render</code> method and in other class methods. Next, you&rsquo;ll create methods to update the state and show dynamic values. </p>

<h2 id="step-3-—-setting-state-from-a-static-value">Step 3 — Setting State from a Static Value</h2>

<p>So far you&rsquo;ve created a base state for the component and you&rsquo;ve referenced that state in your functions and your JSX code. In this step, you&rsquo;ll update your product page to modify the <code>state</code> on button clicks. You&rsquo;ll learn how to pass a new object containing updated values to a special method called <code>setState</code>, which will then set the <code>state</code> with the updated data.</p>

<p>To update <code>state</code>, React developers use a special method called <code>setState</code> that is inherited from the base <code>Component</code> class. The <code>setState</code> method can take either an object or a function as the first argument. If you have a static value that doesn&rsquo;t need to reference the <code>state</code>, it&rsquo;s best to pass an object containing the new value, since it&rsquo;s easier to read. If you need to reference the current state, you pass a function to avoid any references to out-of-date <code>state</code>.</p>

<p>Start by adding an event to the buttons. If your user clicks <strong>Add</strong>, then the program will add the item to the <code>cart</code> and update the <code>total</code>. If they click <strong>Remove</strong>, it will reset the cart to an empty array and the <code>total</code> to <code>0</code>. For example purposes, the program will not allow a user to add an item more then once.</p>

<p>Open <code>Product.js</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/components/Product/Product.js
</li></ul></code></pre>
<p>Inside the component, create a new method called <code>add</code>, then pass the method to the <code>onClick</code> prop for the <strong>Add</strong> button:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

export default class Product extends Component {

state = {
cart: [],
total: 0
}

<span class="highlight">add = () =&gt; {</span>
<span class="highlight">this.setState({</span>
<span class="highlight">cart: ['ice cream'],</span>
<span class="highlight">total: 5</span>
<span class="highlight">})</span>
<span class="highlight">}</span>

currencyOptions = {
minimumFractionDigits: 2,
maximumFractionDigits: 2,
}

getTotal = () =&gt; {
return this.state.total.toLocaleString(undefined, this.currencyOptions)
}

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: {this.state.cart.length} total items.
&lt;/div&gt;
&lt;div&gt;Total {this.getTotal()}&lt;/div&gt;

        &lt;div className="product"&gt;&lt;span role="img" aria-label="ice cream"&gt;🍦&lt;/span&gt;&lt;/div&gt;
        &lt;button onClick=<span class="highlight">{this.add}</span>&gt;Add&lt;/button&gt;
        &lt;button&gt;Remove&lt;/button&gt;
      &lt;/div&gt;
    )

}
}
</code></pre>

<p>Inside the <code>add</code> method, you call the <code>setState</code> method and pass an object containing the updated <code>cart</code> with a single item <code>ice cream</code> and the updated price of <code>5</code>. Notice that you again used an arrow function to create the <code>add</code> method. As mentioned before, this will ensure the function has the proper <code>this</code> context when running the update. If you add the function as a method without using the arrow function, the <code>setState</code> would not exist without <a href="https://www.digitalocean.com/community/conceptual_articles/understanding-this-bind-call-and-apply-in-javascript">binding</a> the function to the current context.</p>

<p>For example, if you created the <code>add</code> function this way:</p>
<pre class="code-pre "><code class="code-highlight language-javascript">export default class Product extends Component {
...
  add() {
    this.setState({
      cart: ['ice cream'],
      total: 5
    })
  }
...
}
</code></pre>
<p>The user would get an error when they click on the <strong>Add</strong> button.</p>

<p><img src="https://assets.digitalocean.com/articles/67228/context-error.png" alt="Context Error"></p>

<p>Using an arrow function ensures that you&rsquo;ll have the proper context to avoid this error.</p>

<p>Save the file. When you do, the browser will reload, and when you click on the <strong>Add</strong> button the cart will update with the current amount.</p>

<p><img src="https://assets.digitalocean.com/articles/67228/see-state-updated.gif" alt="Click on the button and see state updated"></p>

<p>With the <code>add</code> method, you passed both properties of the <code>state</code> object: <code>cart</code> and <code>total</code>. However, you do not always need to pass a complete object. You only need to pass an object containing the properties that you want to update, and everything else will stay the same.</p>

<p>To see how React can handle a smaller object, create a new function called <code>remove</code>. Pass a new object containing just the <code>cart</code> with an empty array, then add the method to the <code>onClick</code> property of the <strong>Remove</strong> button:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

export default class Product extends Component {

...
<span class="highlight">remove = () =&gt; {</span>
<span class="highlight">this.setState({</span>
<span class="highlight">cart: []</span>
<span class="highlight">})</span>
<span class="highlight">}</span>

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: {this.state.cart.length} total items.
&lt;/div&gt;
&lt;div&gt;Total {this.getTotal()}&lt;/div&gt;

        &lt;div className="product"&gt;&lt;span role="img" aria-label="ice cream"&gt;🍦&lt;/span&gt;&lt;/div&gt;
        &lt;button onClick={this.add}&gt;Add&lt;/button&gt;
        &lt;button <span class="highlight">onClick={this.remove}</span>&gt;Remove&lt;/button&gt;
      &lt;/div&gt;
    )

}
}
</code></pre>

<p>Save the file. When the browser refreshes, click on the <strong>Add</strong> and <strong>Remove</strong> buttons. You&rsquo;ll see the cart update, but not the price. The <code>total</code> state value is preserved during the update. This value is only preserved for example purposes; with this application, you would want to update both properties of the <code>state</code> object. But you will often have components with stateful properties that have different responsibilities, and you can make them persist by leaving them out of the updated object.</p>

<p>The change in this step was static. You knew exactly what the values would be ahead of time, and they didn&rsquo;t need to be recalculated from <code>state</code>. But if the product page had many products and you wanted to be able to add them multiple times, passing a static object would provide no guarantee of referencing the most up-to-date <code>state</code>, even if your object used a <code>this.state</code> value. In this case, you could instead use a function.</p>

<p>In the next step, you&rsquo;ll update <code>state</code> using functions that reference the current state.</p>

<h2 id="step-4-—-setting-state-using-current-state">Step 4 — Setting State Using Current State</h2>

<p>There are many times when you&rsquo;ll need to reference a previous state to update a current state, such as updating an array, adding a number, or modifying an object. To be as accurate as possible, you need to reference the most up-to-date <code>state</code> object. Unlike updating <code>state</code> with a predefined value, in this step you&rsquo;ll pass a function to the <code>setState</code> method, which will take the current state as an argument. Using this method, you will update a component&rsquo;s state using the current state.</p>

<p>Another benefit of setting <code>state</code> with a function is increased reliability. To improve performance, React may batch <code>setState</code> calls, which means that <code>this.state.<span class="highlight">value</span></code> may not be fully reliable. For example, if you update <code>state</code> quickly in several places, it is possible that a value could be out of date. This can happen during data fetches, form validations, or any situation where several actions are occurring in parallel. But using a function with the most up-to-date <code>state</code> as the argument ensures that this bug will not enter your code.</p>

<p>To demonstrate this form of state management, add some more items to the product page. First, open the <code>Product.js</code> file:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">nano src/components/Product/Product.js
</li></ul></code></pre>
<p>Next, create an array of objects for different products. The array will contain the product emoji, name, and price. Then loop over the array to display each product with an <strong>Add</strong> and <strong>Remove</strong> button:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

<span class="highlight">const products = [</span>
<span class="highlight">{</span>
<span class="highlight">emoji: '🍦',</span>
<span class="highlight">name: 'ice cream',</span>
<span class="highlight">price: 5</span>
<span class="highlight">},</span>
<span class="highlight">{</span>
<span class="highlight">emoji: '🍩',</span>
<span class="highlight">name: 'donuts',</span>
<span class="highlight">price: 2.5,</span>
<span class="highlight">},</span>
<span class="highlight">{</span>
<span class="highlight">emoji: '🍉',</span>
<span class="highlight">name: 'watermelon',</span>
<span class="highlight">price: 4</span>
<span class="highlight">}</span>
<span class="highlight">];</span>

export default class Product extends Component {

...

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: {this.state.cart.length} total items.
&lt;/div&gt;
&lt;div&gt;Total {this.getTotal()}&lt;/div&gt;
<span class="highlight">&lt;div&gt;</span>
<span class="highlight">{products.map(product =&gt; (</span>
<span class="highlight">&lt;div key={product.name}&gt;</span>
&lt;div className="product"&gt;
&lt;span role="img" aria-label=<span class="highlight">{product.name}</span>&gt;<span class="highlight">{product.emoji}</span>&lt;/span&gt;
&lt;/div&gt;
&lt;button onClick={this.add}&gt;Add&lt;/button&gt;
&lt;button onClick={this.remove}&gt;Remove&lt;/button&gt;
<span class="highlight">&lt;/div&gt;</span>
<span class="highlight">))}</span>
<span class="highlight">&lt;/div&gt;</span>
&lt;/div&gt;
)
}
}
</code></pre>

<p>In this code, you are using the <a href="https://www.digitalocean.com/community/tutorials/how-to-use-array-methods-in-javascript-iteration-methods#map()"><code>map()</code> array method</a> to loop over the <code>products</code> array and return the JSX that will display each element in your browser.</p>

<p>Save the file. When the browser reloads, you&rsquo;ll see an updated product list:</p>

<p><img src="https://assets.digitalocean.com/articles/67228/product-list.png" alt="Product list"></p>

<p>Now you need to update your methods. First, change the <code>add()</code> method to take the <code>product</code> as an argument. Then instead of passing an object to <code>setState()</code>, pass a function that takes the <code>state</code> as an argument and returns an object that has the <code>cart</code> updated with the new product and the <code>total</code> updated with the new price:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

...

export default class Product extends Component {

state = {
cart: [],
total: 0
}

add = (<span class="highlight">product</span>) =&gt; {
this.setState(<span class="highlight">state =&gt; (</span>{
cart: [<span class="highlight">...state.cart, product.name</span>],
total: <span class="highlight">state.total + product.price</span>
})<span class="highlight">)</span>
}

currencyOptions = {
minimumFractionDigits: 2,
maximumFractionDigits: 2,
}

getTotal = () =&gt; {
return this.state.total.toLocaleString(undefined, this.currencyOptions)
}

remove = () =&gt; {
this.setState({
cart: []
})
}

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: {this.state.cart.length} total items.
&lt;/div&gt;
&lt;div&gt;Total {this.getTotal()}&lt;/div&gt;

        &lt;div&gt;
          {products.map(product =&gt; (
            &lt;div key={product.name}&gt;
              &lt;div className="product"&gt;
                &lt;span role="img" aria-label={product.name}&gt;{product.emoji}&lt;/span&gt;
              &lt;/div&gt;
              &lt;button onClick={<span class="highlight">() =&gt; this.add(product)</span>}&gt;Add&lt;/button&gt;
              &lt;button onClick={this.remove}&gt;Remove&lt;/button&gt;
            &lt;/div&gt;
          ))}
        &lt;/div&gt;
      &lt;/div&gt;
    )

}
}
</code></pre>

<p>Inside the anonymous function that you pass to <code>setState()</code>, make sure you reference the argument—<code>state</code>—and not the component&rsquo;s state—<code>this.state</code>. Otherwise, you still run a risk of getting an out-of-date <code>state</code> object. The <code>state</code> in your function will be otherwise identical.</p>

<p>Take care not to directly mutate state. Instead, when adding a new value to the <code>cart</code>, you can add the new <code>product</code> to the <code>state</code> by using the <a href="https://www.digitalocean.com/community/tutorials/understanding-destructuring-rest-parameters-and-spread-syntax-in-javascript#spread">spread syntax</a> on the current value and adding the new value onto the end.</p>

<p>Finally, update the call to <code>this.add</code> by changing the <code>onClick()</code> prop to take an anonymous function that calls <code>this.add()</code> with the relevant product.</p>

<p>Save the file. When you do, the browser will reload and you&rsquo;ll be able to add multiple products.</p>

<p><img src="https://assets.digitalocean.com/articles/67228/adding-products.gif" alt="Adding products"></p>

<p>Next, update the <code>remove()</code> method. Follow the same steps: convert <code>setState</code> to take a function, update the values without mutating, and update the <code>onChange()</code> prop:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

...

export default class Product extends Component {

...

remove = (<span class="highlight">product</span>) =&gt; {
this.setState(<span class="highlight">state =&gt; </span>{
<span class="highlight">const cart = [...state.cart];</span>
<span class="highlight">cart.splice(cart.indexOf(product.name))</span>
<span class="highlight">return ({</span>
<span class="highlight">cart,</span>
<span class="highlight">total: state.total - product.price</span>
<span class="highlight">})</span>
})
}

render() {
return(
&lt;div className="wrapper"&gt;
&lt;div&gt;
Shopping Cart: {this.state.cart.length} total items.
&lt;/div&gt;
&lt;div&gt;Total {this.getTotal()}&lt;/div&gt;
&lt;div&gt;
{products.map(product =&gt; (
&lt;div key={product.name}&gt;
&lt;div className="product"&gt;
&lt;span role="img" aria-label={product.name}&gt;{product.emoji}&lt;/span&gt;
&lt;/div&gt;
&lt;button onClick={() =&gt; this.add(product)}&gt;Add&lt;/button&gt;
&lt;button onClick={<span class="highlight">() =&gt; this.remove(product)</span>}&gt;Remove&lt;/button&gt;
&lt;/div&gt;
))}
&lt;/div&gt;
&lt;/div&gt;
)
}
}
</code></pre>

<p>To avoid mutating the state object, you must first make a copy of it using the <code>spread</code> operator. Then you can <a href="https://www.digitalocean.com/community/tutorials/how-to-use-array-methods-in-javascript-mutator-methods#splice()">splice</a> out the item you want from the copy and return the copy in the new object. By copying <code>state</code> as the first step, you can be sure that you will not mutate the <code>state</code> object.</p>

<p>Save the file. When you do, the browser will refresh and you&rsquo;ll be able to add and remove items:</p>

<p><img src="https://assets.digitalocean.com/articles/67228/remove-items.gif" alt="Remove items"></p>

<p>There is still a bug in this application: In the <code>remove</code> method, a user can subtract from the <code>total</code> even if the item is not in the <code>cart</code>. If you click <strong>Remove</strong> on the ice cream without adding it to your cart, your total will be <strong>-5.00</strong>.</p>

<p>You can fix the bug by checking for an item&rsquo;s existence before subtracting, but an easier way is to keep your state object small by only keeping references to the products and not separating references to products and total cost. Try to avoid double references to the same data. Instead, store the raw data in <code>state</code>— in this case the whole <code>product</code> object—then perform the calculations outside of the <code>state</code>.</p>

<p>Refactor the component so that the <code>add()</code> method adds the whole object, the <code>remove()</code> method removes the whole object, and the <code>getTotal</code> method uses the <code>cart</code>:</p>
<div class="code-label " title="state-class-tutorial/src/components/Product/Product.js">state-class-tutorial/src/components/Product/Product.js</div><pre class="code-pre "><code class="code-highlight language-javascript">import React, { Component } from 'react';
import './Product.css';

...

export default class Product extends Component {

state = {
cart: [],
<span class="highlight">}</span>

add = (product) =&gt; {
this.setState(state =&gt; ({
cart: [...state.cart, <span class="highlight">product</span>],
<span class="highlight">}))</span>
}

currencyOptions = {
minimumFractionDigits: 2,
maximumFractionDigits: 2,
}

getTotal = () =&gt; {
<span class="highlight">const total = this.state.cart.reduce((totalCost, item) =&gt; totalCost + item.price, 0);</span>
return <span class="highlight">total</span>.toLocaleString(undefined, this.currencyOptions)
}

remove = (product) =&gt; {
this.setState(state =&gt; {
const cart = [...state.cart];
<span class="highlight">const productIndex = cart.findIndex(p =&gt; p.name === product.name);</span>
<span class="highlight">if(productIndex &lt; 0) {</span>
<span class="highlight">return;</span>
<span class="highlight">}</span>
cart.splice(<span class="highlight">productIndex, 1</span>)
return ({
cart
<span class="highlight">})</span>
})
}

render() {
...
}
}
</code></pre>

<p>The <code>add()</code> method is similar to what it was before, except that reference to the <code>total</code> property has been removed. In the <code>remove()</code> method, you find the index of the <code>product</code> with <code>findByIndex</code>. If the index doesn&rsquo;t exist, you&rsquo;ll get a <code>-1</code>. In that case, you use a <a href="https://www.digitalocean.com/community/tutorials/how-to-write-conditional-statements-in-javascript">conditional statement</a> toreturn nothing. By returning nothing, React will know the <code>state</code> didn&rsquo;t change and won&rsquo;t trigger a re-render. If you return <code>state</code> or an empty object, it will still trigger a re-render.</p>

<p>When using the <code>splice()</code> method, you are now passing <code>1</code> as the second argument, which will remove one value and keep the rest.</p>

<p>Finally, you calculate the <code>total</code> using the <a href="https://www.digitalocean.com/community/tutorials/list-processing-with-map-filter-and-reduce"><code>reduce()</code></a> array method.</p>

<p>Save the file. When you do, the browser will refresh and you&rsquo;ll have your final <code>cart</code>:</p>

<p><img src="https://assets.digitalocean.com/articles/67228/add-and-remove.gif" alt="Add and remove"></p>

<p>The <code>setState</code> function you pass can have an additional argument of the current props, which can be helpful if you have state that needs to reference the current props. You can also pass a callback function to <code>setState</code> as the second argument, regardless of if you pass an object or function for the first argument. This is particularly useful when you are setting <code>state</code> after fetching data from an API and you need to perform a new action after the <code>state</code> update is complete.</p>

<p>In this step, you learned how to update a new state based on the current state. You passed a function to the <code>setState</code> function and calculated new values without mutating the current state. You also learned how to exit a <code>setState</code> function if there is no update in a manner that will prevent a re-render, adding a slight performance enhancement.</p>

<h2 id="conclusion">Conclusion</h2>

<p>In this tutorial, you have developed a class-based component with a dynamic state that you&rsquo;ve updated statically and using the current state. You now have the tools to make complex projects that respond to users and dynamic information. </p>

<p>React does have a way to manage state with Hooks, but it is helpful to understand how to use state on components if you need to work with components that must be class-based, such as those that use the <code>componentDidCatch</code> method.</p>

<p>Managing state is key to nearly all components and is necessary for creating interactive applications. With this knowledge you can recreate many common web components, such as sliders, accordions, forms, and more. You will then use the same concepts as you build applications using hooks or develop components that pull data dynamically from APIs.</p>

<p>If you would like to look at more React tutorials, check out our <a href="https://www.digitalocean.com/community/tags/react">React Topic page</a>, or return to the <a href="https://www.digitalocean.com/community/tutorial_series/how-to-code-in-react-js">How To Code in React.js series page</a>.</p>
