
  //Simple animated example of d3-cloud - https://github.com/jasondavies/d3-cloud
  //Based on https://github.com/jasondavies/d3-cloud/blob/master/examples/simple.html

  // Encapsulate the word cloud functionality
  function wordCloud(selector,a,b,c,d) {

      var fill = d3.scale.category20();

      //Construct the word cloud's SVG element
      var svg = d3.select(selector).append("svg")
          .attr("width", a)
          .attr("height", b)
          .append("g")
          .attr("transform", "translate("+c+","+d+")");


      //Draw the word cloud
      function draw(words) {
          var cloud = svg.selectAll("g text")
                          .data(words, function(d) { return d.text; })

          //Entering words
          cloud.enter()
              .append("text")
              .style("font-family", "Impact")
              .style("fill", function(d, i) { return fill(i); })
              .attr("text-anchor", "middle")
              .attr('font-size', 1)
              .text(function(d) { return d.text; });

          //Entering and existing words
          cloud
              .transition()
                  .duration(600)
                  .style("font-size", function(d) { return d.size + "px"; })
                  .attr("transform", function(d) {
                      return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                  })
                  .style("fill-opacity", 1);

          //Exiting words
          cloud.exit()
              .transition()
                  .duration(200)
                  .style('fill-opacity', 1e-6)
                  .attr('font-size', 1)
                  .remove();
      }


      //Use the module pattern to encapsulate the visualisation code. We'll
      // expose only the parts that need to be public.
      return {

          //Recompute the word cloud for a new set of words. This method will
          // asycnhronously call draw when the layout has been computed.
          //The outside world will need to call this function, so make it part
          // of the wordCloud return value.
          update: function(words) {
              d3.layout.cloud().size([200, 200])
                  .words(words)
                  .padding(2)
                  .rotate(function() { return ~~(Math.random() * 2) * 90; })
                  .font("Impact")
                  .fontSize(function(d) { return d.size; })
                  .on("end", draw)
                  .start();
          }
      }

  }

  //Prepare one of the sample sentences by removing punctuation,
  // creating an array of words and computing a random size attribute.
  function getWords(words) {
      return words
              .replace(/[!\.,:;\?]/g, '')
              .split(' ')
              .map(function(d) {
                  return {text: d, size: 25};
              })
  }

  //This method tells the word cloud to redraw with a new set of words.
  //In reality the new words would probably come from a server request,
  // user input or some other source.
  function showNewWords(vis, words) {
      vis.update(getWords(words))
  }
