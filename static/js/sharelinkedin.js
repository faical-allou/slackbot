// Setup an event listener to make an API call once auth is complete
function onLinkedInLoad() {
}

// Handle the successful return from the API call
function onSuccess(data) {
  setTimeout( function () {
    swal({
      title:"Posted!",
      text: "You can find the post <strong><a href="+data.updateUrl+" target='_blank'>here</a></strong> when it is ready.",
      type: "success",
      html: true
      });
    }, 4000)
  mixpanel.track("Sharing success", {"Page":viewpage, "Post":data.updateUrl});
}

// Handle an error response from the API call
function onError(error) {
  console.log(error);
  if (error.message == "Invalid arguments: {S_400_BAD_REQUEST=Bad request}")
    {
      swal({
        title:'Please "Sign in with Linkedin" first',
        text: "use the button at the bottom of the page to authorize posting from this page",
        type: "error",
        html: true
        }
      );
      mixpanel.track("Sharing not logged in", {"Page":viewpage});
    }
    else
    {
      swal({
        title: "Error...",
        text: "Linkedin refused your post. </br><i>"+error.message+"</i> </br>We'll do what we can to fix this asap.",
        type: "error",
        html: true
        }
      );
      mixpanel.track("Sharing error", {"Page":viewpage, "Error": error.message});
    }
}
// Use the API call wrapper to share content on LinkedIn
function shareContent(urlToPrint, subtitle) {
  urlEncoded = encodeURIComponent(urlToPrint);
  //screenshotURL = "http://api.screenshotmachine.com/?key=54021f&dimension=720x600&format=png&cacheLimit=0&timeout=3000&url=" + urlEncoded;
  screenshotURL = "http://api.screenshotlayer.com/api/capture?access_key=3ea44b15b4158e350c0751b133a84b18&viewport=720x700&delay=3&url="+urlEncoded;
  console.log(screenshotURL);
  swal({
    title: "Post this view to Linkedin",
    text: "This will be visible publicly on your profile",
    type: "input",
    showCancelButton: true,
    confirmButtonColor: "#5be2ed",
    confirmButtonText: "Post to my profile",
    inputPlaceholder: "add a comment",
    closeOnConfirm: false,
    showLoaderOnConfirm: true,
    },
    function(inputTextPost){
        mixpanel.track("Sharing open", {"Page":viewpage});

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
