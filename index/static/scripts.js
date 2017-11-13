$(window).on('popstate', function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $(".site-content").hide();
    $(".site-content").html(state.context);
    $(".site-content").fadeIn();
    $("title")[0].innerText = state.title;
    if (state.q) {
      $("#q").val(state.q);
    }
  }
});

// using jQuery
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function refreshCookie() {
  // for sending csrf token on every ajax POST request
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
}

function refreshPage() {
  // refresh navbar (and maybe other stuff as well?)
  // csrf token gets passed because home needs it (stupid?)
  $.ajax({
    type: "GET",
    url: "/navbar/",
    error: function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    },
    success: function(response) {
      // refresh navbar
      $(".nav-content").html(response);
      // TODO go to index
      var url = "/";
      $.ajax({
        type: "POST",
        url: url,
        error: function(xhr, ajaxOptions, thrownError){
          console.log(thrownError);
        },
        success: function(response) {
          var title = "dopepod";
          var state = {
            "context": response,
            "title": title,
          };
          history.pushState(state, "", url);
          $(".site-content").hide();
          $(".site-content").html(response);
          $(".site-content").fadeIn();
          $("title")[0].innerText = title;
        }
      });
    }
  });
}

// wait until user stops typing
// credit: https://remysharp.com/2010/07/21/throttling-function-calls/
function debounce(fn, delay) {
  var timer = null;
  return function () {
    var context = this, args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fn.apply(context, args);
    }, delay);
  };
}

// ye ajax search function
function SearchFunc() {
  // minlength for search string
  var minlength = 2
  // gather variables
  var q = $(".site-content #q").val();
  // TODO fix these selectors
  var genre = $(".site-content .search-options").val();
  var language = $(".site-content .search-options").val();
  var explicit = $(".site-content .search-options").is(":checked");
  // if input is at least minlength, go ahead and search
  if(q.length >= minlength) {
    $.ajax({
      method: "POST",
      url: "/podcasts/search/",
      data: {
        "q": q,
        "genre": genre,
        "language": language,
        "explicit": explicit,
      },
      error: function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
      },
      success: function(response) {
        $("#results").hide();
        $("#results").html(response);
        $("#results").fadeIn();

        // save results + q in current state
        // TODO results is still mostly hidden
        // removing style (hacky)
        $("#results").removeAttr("style");
        var curContext = $("#site-content")[0].innerHTML;
        var curUrl = $("#site-content")[0].baseURI;
        var curTitle = "dopepod";
        var curState = {
          "context": curContext,
          "title": curTitle,
          "q": q,
        };
        history.replaceState(curState, "", curUrl);
      }
    });
  }
  // else show nothing
  else {
    $("#results").hide();
    $("#results").html("");
    $("#results").fadeIn();

    // save results + q in current state
    // TODO results is still mostly hidden
    // removing style (hacky)
    $("#results").removeAttr("style");
    var curContext = $("#site-content")[0].innerHTML;
    var curUrl = $("#site-content")[0].baseURI;
    var curTitle = "dopepod";
    var curState = {
      "context": curContext,
      "title": curTitle,
      "q": q,
    };
    history.replaceState(curState, "", curUrl);
  }
}

$(document).ready(function() {
  refreshCookie();
});

// search when user types into search field (with min "delay" between keypresses)
var delay = 250
$(document).on("keyup", "#q", debounce(SearchFunc, delay));

// search when "search" button is clicked
$(document).on("submit", "#search-form", function (e) {
  e.preventDefault();
  debounce(SearchFunc, delay);
});

  // search when user changes options
$(document).on("change", ".search-options", SearchFunc);

$(document).on("click", ".show-podinfo", function(e) {
  e.preventDefault();
  var itunesid = this.id;
  var ajax_url = "/podcasts/podinfo/";
  $.ajax({
    type: "POST",
    url: ajax_url,
    data: {
      "itunesid": itunesid,
    },
    error: function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    },
    success: function(response) {
      var title = "podinfo";
      var state = {
        "context": response,
        "title": title,
      };
      var url = ajax_url + itunesid + "/";
      history.pushState(state, "", url);
      $("#site-content").hide();
      $("#site-content").html(response);
      $("#site-content").fadeIn();
      $("title")[0].innerText = title;

      // load tracks for podcast
      // TODO also load on back button
      var url = "/podcasts/tracks/";
      $.ajax({
        method: "POST",
        url: url,
        data: {
          "itunesid": itunesid,
        },
        error: function(xhr, ajaxOptions, thrownError){
          console.log(thrownError);
        },
        success: function(response) {
          $("#tracks").hide();
          $("#tracks").html(response);
          $('#overlay').addClass('hide');
          $("#tracks").fadeIn();
        }
      });
    }
  });
});

$(document).on("submit", ".profile-form", function (e) {
  e.preventDefault();
  var data = $(this).serialize();
  var method = this.method;
  var url = this.action;
  $.ajax({
    data: data,
    method: method,
    url: url,
    error: function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
      $(".modal-content").html(xhr.responseJSON.html);
    },
    success: function(response) {
      $(".modal-content").html("");
      $("#modal").modal("hide");
    }
  });
});

$(document).on("click", ".ajax-login, .ajax-register", function(e) {
  e.preventDefault();
  var url = this.href;
  var method = this.method;
  $.ajax({
    type: method,
    url: url,
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(response) {
      $(".modal-content").html(response.html);
    }
  });
});

$(document).on("click", ".home", function(e) {
  e.preventDefault();
  var url = "/";
  $.ajax({
    type: "POST",
    url: url,
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(response) {
      var title = "dopepod";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $(".site-content").hide();
      $(".site-content").html(response);
      $(".site-content").fadeIn();
      $("title")[0].innerText = title;
    }
  });
});

$(document).on("click", ".settings", function(e) {
  e.preventDefault();
  var url = "/settings/";
  $.ajax({
    type: "GET",
    url: url,
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(response) {
      $(".modal-content").html(response);
    }
  });
});

$(document).on("click", ".subscriptions", function(e) {
  e.preventDefault();
  var url = "/subscriptions/";
  $.ajax({
    type: "POST",
    url: url,
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(response) {
      var title = "subscriptions";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $(".site-content").hide();
      $(".site-content").html(response);
      $(".site-content").fadeIn();
      $("title")[0].innerText = title;

      // load subscriptions
      $.ajax({
        type: "POST",
        url: url,
        data: {
          "ajax": "yep",
        },
        error: function(xhr, ajaxOptions, thrownError){
          console.log(thrownError);
        },
        success: function(response) {
          $("#subscriptions").html(response);
        }
      });
    }
  });
});

$(document).on("click", ".browse", function(e) {
  e.preventDefault();
  var url = "/browse/";
  $.ajax({
    type: "POST",
    url: url,
    data: {
      "ajax": "yep",
    },
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(response) {
      var title = "browse";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $(".site-content").hide();
      $(".site-content").html(response);
      $(".site-content").fadeIn();
      $("title")[0].innerText = title;
    }
  });
});

  $(document).on("click", ".play", function() {
  var url = this.id;
  var type = this.name;
  $.ajax({
    method: "POST",
    url: "/podcasts/play/",
    data: {
      "url": url,
      "type": type,
    },
    success: function(response) {
      $("#player").hide();
      $("#player").html(response);
      $("#player").fadeIn();
    }
  })
});

// TODO check if subscribed or nah
// subscription button
$(document).on("submit", "#sub-form", function(e) {
  // Stop form from submitting normally
  e.preventDefault();
  var itunesid = this.id;
  var button = $("#sub-button");
  var url = "/subscribe/";
  $.ajax({
    method: "POST",
    url: url,
    data: {
      "itunesid": itunesid,
    },
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(data) {
      button.val(data);
    }
  });
});

$(document).on("click", ".login-link, .signup-link", function(e) {
  e.preventDefault();
  var url = this.href;
  $.ajax({
    method: method,
    url: url,
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function(response) {
      $(".modal-content").html(response.html);
    }
  });
});

$(document).on("submit", ".login-form, .signup-form", function (e) {
  e.preventDefault();
  var data = $(this).serialize();
  var method = this.method;
  var url = this.action;
  $.ajax({
    data: data,
    method: method,
    url: url,
    error: function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
      $(".modal-content").html(xhr.responseJSON.html);
    },
    success: function() {
      $("#modal").modal("hide");
      refreshCookie();
      refreshPage();
    }
  });
});

$(document).on("click", ".ajax-logout", function(e) {
  e.preventDefault();
  $.ajax({
    type: "GET",
    url: "/account/logout/",
    error: function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    },
    success: function() {
      refreshCookie();
      refreshPage();
    }
  });
});
