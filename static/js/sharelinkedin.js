

// Setup an event listener to make an API call once auth is complete
function onLinkedInLoad() {
}

// Handle the successful return from the API call
function onSuccess(data) {
  swal({
    title:"Posted!",
    text: "The post will be visible in few seconds on your profile <strong><a href="+data.updateUrl+" target='_blank'>here</a></strong>",
    type: "success",
    html: true
    }
  );
  mixpanel.track("Sharing success", {"Page":viewpage; "Post":data.updateUrl});

}

// Handle an error response from the API call
function onError(error) {
  console.log(error);
  if (error.message == "Invalid arguments: {S_400_BAD_REQUEST=Bad request}")
    {
      swal({
        title:"Please log in first",
        text: "It looks like you are not logged in on <strong><a href=http://www.linkedin.com target='_blank'>Linkedin</a></strong>",
        type: "error",
        html: true
        }
      );
      mixpanel.track("Sharing not logged in", {"Page":viewpage});

    }
    else
    {
      swal("Error...", "Linkedin refused your post. Please check that you are logged in. We'll do what we can to fix this asap. "+error.message, "error");
      mixpanel.track("Sharing error", {"Page":viewpage; "Error": error.message});
    }
}

// Use the API call wrapper to share content on LinkedIn
function shareContent(urlToPrint, subtitle) {
  traveltrendsURLencoded = encodeURIComponent("traveltrends.herokuapp.com/catchment_view?originairport="+window.originairport+"&rangekm="+window.rangekm+"&destinationcity="+window.destinationcity);
  //screenshotURL = "http://api.screenshotmachine.com/?key=54021f&dimension=720x600&format=png&cacheLimit=0&timeout=3000&url=" + traveltrendsURL;
  screenshotURL = "http://api.screenshotlayer.com/api/capture?access_key=3ea44b15b4158e350c0751b133a84b18&viewport=720x750&url="+urlToPrint
  swal({
    title: "Post this view to Linkedin",
    text: "This will be visible publicly on your profile",
    type: "input",
    showCancelButton: true,
    confirmButtonColor: "#5be2ed",
    confirmButtonText: "Post to my profile",
    inputPlaceholder: "add a comment",
    closeOnConfirm: false
    },
    function(inputTextPost){
        if (inputTextPost === false) return false;
        // Build the JSON payload containing the content to be shared
        var payload = {
          "content":{
            "title": subtitle ,
            "description": "check here: https://partners.skyscanner.net/travel-insight-lite",
            "submitted-url": screenshotURL
          },
          "comment": inputTextPost,
          "visibility": {
            "code": "anyone"
          }
        }
        IN.API.Raw("/people/~/shares?format=json")
          .method("POST")
          .body(JSON.stringify(payload))
          .result(onSuccess)
          .error(onError);
      }
  )
};
