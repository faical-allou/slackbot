//definition of standard options for googlecharts
backgroundGraph = { fill: '#FFF' };
widthGraph = 750;
heightGraph = 550;
areaGraph = { width: '70%', height: '80%'};
colorsGraph = ['#00B2D6', '#272133', '#005567'];
vAxisGraph= {textStyle: {color: '#272133', fontName: "Helvetica",fontSize: 16},
            titleTextStyle: {color: '#272133', fontName: "Helvetica",fontSize: 18},
            gridlines: {count: 0}};
hAxisGraph= { minValue: 0,
        baselineColor: '#DFDCE3',
        textStyle: {color: '#272133', fontName: "Helvetica",fontSize: 16},
        titleTextStyle: {color: '#272133', fontName: "Helvetica",fontSize: 18},
        gridlines: {count: 0},
        };
legendGraph= {position: 'none'}; 
curveTypeGraph= 'function';
lineWidthGraph = 4;

standardOptions= {'width': widthGraph,
                  'height':heightGraph,
                  'chartArea': areaGraph,
                  'colors': colorsGraph,
                  'backgroundColor': backgroundGraph,
                  'vAxis': vAxisGraph,
                  'hAxis': hAxisGraph,
                  'legend': legendGraph,
                  'lineWidth': lineWidthGraph,
                  'curveType': curveTypeGraph,
};

// function to autosuggest city or airport codes with validation and message
function autoSuggestInput(inputfield, suggesttype){
  swal_on = 0;
    //type can only be airport or city
  if (suggesttype == "airport") {var sourcetable = availableairports} else {var sourcetable = availablecities};
  $( function() {
    $( "#"+inputfield ).autocomplete({
          source: sourcetable,
          minLength: 2,
          response: function(event,ui)
            {
              if(ui.content.length==1)
              {
                document.getElementById(inputfield).value=ui.content[0].value;
                ui.item = ui.content[0].value;
              };
              if(ui.content.length==0)
              { swal_on = 1;
                swal({  title: "City code <> Airport code",  text: document.getElementById(inputfield).value.toUpperCase()+" is not a valid "+suggesttype.toUpperCase()+" code",  html: true, type: "warning",  confirmButtonText: "OK"}, function() {swal_on=0});
                mixpanel.track("Error reset field", {"Page":viewpage, "input": document.getElementById(inputfield).value });
                $(inputfield).val('');
                $(inputfield).focus();
              };
            }
    });
  });
}

// function to retrieve the city name from the parameters passed in the URL
function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
}

// adding a listener for the enter key only when focus is on the input
function drawOnEnterKey(e) {
        var focused = document.activeElement.id;
        var list_input = ['originAirportInput', 'rangeKmInput','originCityInput', 'destinationCityInput','crossBorderInput' ];
        if (e.keyCode == 13 && list_input.indexOf(focused) >= 0 ) {
            drawChart();
        }
}

function internalError(url_to_call) {
            swal({  title: "Sorry",  text: "Something went wrong, we'll fix it soon",  type: "error",  confirmButtonText: "OK"});
            mixpanel.track("Error internal", {"Page":viewpage, "URL": url_to_call});
}

function notEnoughData(url_to_call){
              swal({  title: "Sorry",  text: "We don't have enough data for this request",  html: true, type: "error",  confirmButtonText: "OK"});
              mixpanel.track("Error data", {"Page":viewpage, "URL": url_to_call});
}
