$(document).ready(function(){
// read after page is build

$("#field").keyup(function(){
  /* one types a query */
  console.log("Input: " + $("#field").val())
  // create url from input
  var host = window.location.hostname;
  var port = window.location.port;
  var query = $("#field").val();
  var url = "http://" + host + ":" + port + "/search.html/api?q=" + query;

  /* send get-request with query.
  After receiving the response call the function, */
  $.get(url, function(response){
    console.log(response);
    //$("#result").html(response.result);
  })
})
})


