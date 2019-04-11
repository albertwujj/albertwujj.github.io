const mediumToMarkdown = require('medium-to-markdown');
// Enter url here
mediumToMarkdown.convertFromUrl("https://medium.com/@albertwu_14963/in-depth-explaining-openais-gpt-2-bc49b6fb8559").then(function (markdown) {
  console.log(markdown); //=> Markdown content of medium post
});
