$(window).on('popstate', function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $("#main-content").html(state.context);
    $("title")[0].innerText = state.title;
    if (state.q) {
      $("#q").val(state.q);
    }
    if (state.alphabet) {
      $("input[name='alphabet'][value='" + state.alphabet + "']").prop("checked", true);
    }
    if (state.view) {
      $("input[name='view'][value='" + state.view + "']").prop("checked", true);
    }
  }
});

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
};

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

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
};

function goToIndex() {
  var url = "/"
  var title = "dopepod"
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#main-content").html(response);
      $(window).scrollTop(0);
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goToPage(url) {
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);
      $(window).scrollTop(0);
      var state = {
        "context": response,
        "title": 'dopepod',
      };
      var url = '/';
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goToModal(url) {
  $.ajax({
    type: "GET",
    url: url,
  })
  .fail(function(xhr, ajaxOptions, thrownError){
    console.log(thrownError);
  })
  .done(function(response) {
    if ($("#modal").css('display') == 'none') {
      $("#modal").modal("show");
    }
    $("#modal-content").html(response.html);
  });
}

function refreshPage() {
  // refresh navbar (and maybe other stuff as well?)
  $.ajax({
    type: "GET",
    url: "/navbar/",
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    })
    .done(function(response) {
      // refresh navbar
      $("#nav-content").html(response);
      // go to index
      goToPage("/");
    });
};

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
};

// ye ajax search function
function SearchFunc() {
  // minlength for search string
  var minlength = 2
  // gather variables
  var q = $("#q").val();

  data = {};
  data['q'] = q;

  // if input is at least minlength, go ahead and search
  if (q.length >= minlength) {
    // if options exists, get values
    if ($("#options").length) {
      var genre = $("input[name='genre']:checked").val();
      var language = $("input[name='language']:checked").val();
      var view = $("input[name='view']:checked").val();

      if (language != 'All') {
        data['language'] = language;
      }
      if (genre != 'All') {
        data['genre'] = genre;
      }
      if (view != 'detail') {
        data['view'] = view;
      }
    }

    $.ajax({
      method: "GET",
      url: "/search/",
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
      })
      .done(function(response) {
        $("#results").html(response);

        // save results + q in current state
        var context = $("#main-content")[0].innerHTML;
        var url = "/search/" + "?" + $.param(data);
        var title = "dopepod";
        var state = {
          "context": context,
          "title": title,
          "data": data,
        };
        history.replaceState(state, "", url);
      });
  }
  // else show nothing
  else {
    $("#results-content").html("");

    // save results + q in current state
    var context = $("#main-content")[0].innerHTML;
    var url = "/search/";
    var title = "dopepod";
    var state = {
      "context": context,
      "title": title,
      "data": data,
    };
    history.replaceState(state, "", url);
  }
};

function BrowseFunc() {
  var alphabet = $("input[name='alphabet']:checked").val();
  data = {};
  data['alphabet'] = alphabet;

  if ($("#options").length) {
    var view = $("input[name='view']:checked").val();
    var genre = $("input[name='genre']:checked").val();
    var language = $("input[name='language']:checked").val();

    if (language != 'All') {
      data['language'] = language;
    }
    if (genre != 'All') {
      data['genre'] = genre;
    }
    if (view != 'list') {
      data['view'] = view;
    }
  }

  $.ajax({
    method: "POST",
    url: "/browse/",
    data: data,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);

      // save results + q in current state
      var context = $("#main-content")[0].innerHTML;
      var url = "/browse/" + "?" + $.param(data);
      var title = "dopepod";
      var state = {
        "context": context,
        "title": title,
        "data": data,
      };
      history.replaceState(state, "", url);
    });
};

function getSubscriptions() {
  // load subscriptions
  var url = "/subscriptions/";
  $.ajax({
    type: "POST",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results-content").html(response);
    });
};

var delay = 250

// after page loads
$(document)
  // refresh cookie
  .ready(refreshCookie())
  // initialize bootstrap tooltips
  .ready($('[data-toggle="tooltip"]').tooltip())
  // search when user types into search field (with min "delay" between keypresses)
  .on("keyup", "#q", debounce(SearchFunc, delay))
  // search when "search" button is clicked
  .on("submit", "#search-form", function(e) {
    e.preventDefault();
    SearchFunc();
  })
  // remove focus from button (focus would be saved on state)
  .on("click", "#search-button, #alphabet-buttons, #genre-buttons, #language-buttons, #view-buttons", function() {
    $(this.children).removeClass("focus");
  })
  // search when user changes options
  .on("change", "#genre-buttons, #language-buttons, #view-buttons", function() {
    if ($("#search-bar").css('display') == 'none') {
      BrowseFunc();
    }
    else {
      SearchFunc();
    }
  })
  .on("change", "#alphabet-buttons", function() {
    BrowseFunc();
  })
  .on("click", "#search-button", function() {
    SearchFunc();
  })
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var url = this.href;
    var url2 = this.href;
    var itunesid = this.id;
    $.ajax({
      type: "GET",
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
      })
      .done(function(response) {
        $("#main-content").html(response);

        var title = "dopepod";
        if ($("#podinfo").length) {
          title = $("#podinfo h1")[0].innerHTML;
        }

        var state = {
          "context": response,
          "title": title,
        };

        $("title")[0].innerText = title;
        history.pushState(state, "", url2);
      });
  })
  // go to home view
  .on("click", ".home-link", function(e) {
    e.preventDefault();
    goToIndex();
    goToPage("/charts/");
  })
  // open browse
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    goToIndex();
    goToPage("/browse/");
    // BrowseFunc();
  })
  .on("click", ".search-toggle", function(e) {
    e.preventDefault();
    $("#search-bar").toggle();
    $("#browse-bar").toggle();
  })
  // open subscriptions
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    goToPage("/subscriptions/", "subscriptions");
    getSubscriptions();
  })
  // open settings in modal
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    goToPage("/settings/", "settings");
  })
  // save settings, empty and hide modal
  .on("submit", ".settings-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
        $("#main-content").html(xhr.responseJSON.html);
      })
      .done(function(response) {
        goToPage("/");
      });
  })
  // put episode in player
  .on("click", ".play", function(e) {
    e.preventDefault();
    var data = $(this).serialize();
    var url = this.action;
    var method = this.method;
    $.ajax({
      method: "POST",
      url: "/play/",
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function(response) {
        $("#player").html(response);
        $("#footer").css("padding-bottom", "106px");
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    $("#player").empty();
    $("#footer").css("padding-bottom", "0px");
  })
  .on("submit", "#sub-form", function(e) {
    // Stop form from submitting normally
    e.preventDefault();

    // button, gets new value
    var button = $(this).find(".sub-button");

    var data = $(this).serialize();
    var url = this.action;
    var method = this.method;
    $.ajax({
      method: method,
      url: url,
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
        // probably not logged in
        goToModal("/account/login/");
      })
      .done(function(response) {
        button.html(response);

        var url = $("#main-content")[0].baseURI;
        var context = $("#main-content")[0].innerHTML;
        if ($("#podinfo").length) {
          var title = $("#podinfo h1")[0].innerHTML;
        }

        var state = {
          "context": context,
          "title": title,
        };
        history.replaceState(state, "", url);
      });
  })
  // open login register or password reset in modal
  .on("click", ".ajax-login, .ajax-register, .login-link, .signup-link, .password-link", function(e) {
    e.preventDefault();
    var url = this.href;
    goToModal(url);
  })
  // login or signup, refresh after
  .on("submit", ".login-form, .signup-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
        $("#modal-content").html(xhr.responseJSON.html);
      })
      .done(function() {
        $("#modal-content").html("");
        $("#modal").modal("hide");
        refreshCookie();
        refreshPage();
      });
  })
  // logout, refresh after
  // .on("click", ".ajax-logout", function(e) {
  //   e.preventDefault();
  //   var url = this.href;
  //   $.ajax({
  //     type: "POST",
  //     url: url,
  //   })
  //   .fail(function(xhr, ajaxOptions, thrownError){
  //     console.log(thrownError);
  //   })
  //   .done(function() {
  //     refreshPage();
  //   });
  // });


var mb = $("#search-form");

$(window).scroll(function() {
  if ($(this).scrollTop() > 50) {
    mb.addClass("fixed");
  }
  else {
    mb.removeClass("fixed");
  }
})
