$(document).ready(function(){
// read after page is build

$("#field").keyup(function(){
  /* one types a query */
  console.log("Input: " + $("#field").val());
  // create url from input
  var host = window.location.hostname;
  var port = window.location.port;
  var query = $("#field").val();
  var url = "http://" + host + ":" + port + "/api?q=" + query;

  /* send get-request with query.
  After receiving the response call the function. */
 $.get(url, function(res){
    console.log("resp: " + res.QUERY);
//    var myObj = JSON.parse(response);
//    console.log(myObj);
    $("#result-header").html(res.QUERY);

  // style all results
  var entity = ""
  for (var i = 0; i < res.ENTITYS.length; i++){ 
    console.log(i)
    var res_e = res.ENTITYS[i];

    entity += '<div class=\"entity\"> ' +
      '  <div class="entity-image"><a target="_blank" href="' +
      res_e.ENTITY_WIKIDATA_URL + '"><img src="' +  res_e.ENTITY_IMG + '"></div></a>' +
      '  <div class="entity-metadata">' +
      '    <div class="entity-header">' +
      '      <div class="entity-name">' + res_e.ENTITY_NAME + '</div>' +
      '      <div class="entity-synonym">' + res_e.ENTITY_SYNONYM + ' + (ped ' + res_e.ENTITY_PED + ', score ' + res_e.ENTITY_SCORE + ')</div>' +
      '    </div>' +
      '    <div class="entity-description">' + res_e.ENTITY_DESC + '</div>' +
      '    <div class="entity-links">' +
      '      External Links:' +
      '      <a target="_blank" href="' + res_e.ENTITY_WIKIDATA_URL + '"><img src="wikidata.png"></a>' +
      '      <a target="_blank" href="' + res_e.ENTITY_WIKIPEDIA_URL + '"><img src="wikipedia.png"></a>' +
      '    </div>' +
      '  </div>' +
      '</div>`';
  }
  // show results
  console.log(entity)
  $("#result-body").html(entity);
  });
});
});


