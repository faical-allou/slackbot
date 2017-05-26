function autoSuggestInput(inputfield, suggesttype){
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
            {swal(document.getElementById(inputfield).value+" is not a valid "+suggesttype.toUpperCase()+" code");
              mixpanel.track("Error reset field", {"Page":viewpage, "input": document.getElementById(inputfield).value });
              $(inputfield).val('');
              $(inputfield).focus();
            };
          }
  });
});
};
