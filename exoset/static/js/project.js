

// variable that keeps all the filter information

var send_data = {}

$(document).ready(function () {
    // reset all parameters on page load
    $('[data-toggle="tooltip"]').tooltip();
    resetFilters();
    // bring all the data without any filters

    getAPIData();
    // get all countries from database via

    // AJAX call into country select options

    //getAuthors();
    // get all varities from database via

    // AJAX call into variert select options

    getLevels();
    getTagFamily();
    getCourse();
    getLanguage();
    getOntology();


    $('#levels').on('change', function () {


        if(this.value == "all")
            send_data['level'] = "";
        else
            send_data['level'] = this.value;

        getAPIData();
    });
    $('#families').on('change', function () {


        if(this.value == "all")
            send_data['tagproblemtype'] = "";
        else
            send_data['tagproblemtype'] = this.value;

        getAPIData();
    });
    $('#courses').on('change', function () {


        if(this.value == "all")
            send_data['course'] = "";
        else
            send_data['course'] = this.value;


        getAPIData();
    });
    $('#tags').on('change', function () {


        if(this.value == "all")
            send_data['concept'] = "";
        else
            send_data['concept'] = this.value;

        getAPIData();
    });
    $('#languages').on('change', function () {


        if(this.value == "all")
            send_data['language'] = "";
        else
            send_data['language'] = this.value;

        getAPIData();
    });
    $('#ontologies').on('click', function () {


        if(this.value == "all")
            send_data['ontology'] = "";
        else
            send_data['ontology'] = this.value;

        getAPIData();
    });
    $('#sort_by').on('change', function () {
        send_data['sort_by'] = this.value;
        getAPIData();
    });

    // display the results after reseting the filters

    $("#display_all").click(function(){
        resetFilters();
        getAPIData();
    })
})


/**
    Function that resets all the filters
**/
function resetFilters() {
    $("#ontologies").val("all");
    $("#tags").val("");
    $("#languages").val("all");
    $("#courses").val("all");
    $("#families").val("all");
    $("#levels").val("all");
    send_data['ontology'] = "";
    send_data['concept'] = "";
    send_data['language'] = "";
    send_data['course'] = "";
    send_data['tagproblemtype'] = "";
    send_data['level'] = "";
    getAPIData();

}

/**.
    Utility function to showcase the api data
    we got from backend to the table content
**/
function putTableData(result) {
    // creating table row for each result and

    // pushing to the html cntent of table body of listing table

    let row;
    if(result["results"].length > 0){
        $("#no_results").hide();
        $("#list_data").show();
        $("#listing").html("");
        $.each(result["results"], function (a, b) {
            var url_mask = b.slug;

            row = "<tr> "  + "<td style='width: 13%' title=\"" + b.title + "\">" + b.title.slice(0, 50) + "..." + "</td>"+
                "<td style='width: 13%'>" + b.family_problem +
                "</td><td style='width: 18%'>" + b.ontology_path  +
                "</td><td style='width: 11%'>" + b.tag_concept  +
                "</td><td style='width: 13%'>" + b.related_courses +
                "</td><td style='width: 8%'>" + b.tag_level +
                "</td><td style='width: 15%'>" + b.prerequisite_assigned +
                "</td><td style='width: 20%'>" + b.tag_question_type +
                "</td><td style='width: 4%'> <a href=\"" + url_mask  + "\">Voir</a></td></tr>"
            $("#listing").append(row);
        });
    }
    else{
        // if no result found for the given filter, then display no result

        $("#no_results h5").html("No results found");
        $("#list_data").hide();
        $("#no_results").show();
    }
    // setting previous and next page url for the given result

    let prev_url = result["previous"];
    let next_url = result["next"];
    // disabling-enabling button depending on existence of next/prev page.

    if (prev_url === null) {
        $("#previous").addClass("disabled");
        $("#previous").prop('disabled', true);
    } else {
        $("#previous").removeClass("disabled");
        $("#previous").prop('disabled', false);
    }
    if (next_url === null) {
        $("#next").addClass("disabled");
        $("#next").prop('disabled', true);
    } else {
        $("#next").removeClass("disabled");
        $("#next").prop('disabled', false);
    }
    // setting the url

    $("#previous").attr("url", result["previous"]);
    $("#next").attr("url", result["next"]);
    // displaying result count

    $("#result-count span").html(result["count"]);
}

function getAPIData() {
    let url = $('#list_data').attr("url")
    $.ajax({
        method: 'GET',
        url: url,
        data: send_data,
        beforeSend: function(){
            $("#no_results h5").html("Loading data...");
        },
        success: function (result) {
            putTableData(result);
        },
        error: function (response) {
            $("#no_results h5").html("Something went wrong");
            $("#list_data").hide();
        }
    });
}

$("#next").click(function () {
    // load the next page data and

    // put the result to the table body

    // by making ajax call to next available url

    let url = $(this).attr("url");
    if (!url)
        $(this).prop('all', true);

    $(this).prop('all', false);
    $.ajax({
        method: 'GET',
        url: url,
        success: function (result) {
            putTableData(result);
        },
        error: function(response){
            console.log(response)
        }
    });
})

$("#previous").click(function () {
    // load the previous page data and

    // put the result to the table body

    // by making ajax call to previous available url

    let url = $(this).attr("url");
    if (!url)
        $(this).prop('all', true);

    $(this).prop('all', false);
    $.ajax({
        method: 'GET',
        url: url,
        success: function (result) {
            putTableData(result);
        },
        error: function(response){
            console.log(response)
        }
    });
})

function getAuthors() {
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#resources").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {

            authorss_option = "<option value='all' selected>All authors</option>";
            $.each(result["authors"], function (a, b) {
                authorss_option += "<option>" + b + "</option>"
            });
            $("#resources").html(authorss_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}

function getLevels() {
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#levels").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            levels_option = "<option value='all' selected>All levels</option>";
            $.each(result["levels"], function (a, b) {
                levels_option += "<option value='" + b[1] + "'>" + b[0] + "</option>"
            });
            $("#levels").html(levels_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}

function getCourse() {
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#courses").attr("url");

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            courses_option = "<option value='all' selected>All sectors</option>";
            $.each(result["courses"], function (a, b) {
                courses_option += "<option value='" +b[1] + "'>" + b[0] + "</option>"
            });
            $("#courses").html(courses_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}

function getTagFamily() {
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#families").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            tag_families_option = "<option value='all' selected>All problem types</option>";
            $.each(result["tag_families"], function (a, b) {
                tag_families_option += "<option value='" +b[1] + "'>" + b[0] + "</option>"
            });
            $("#families").html(tag_families_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}

function getLanguage() {
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#languages").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            languagess_option = "<option value='all' selected>All languages</option>";
            $.each(result["languages"], function (a, b) {
                languagess_option += "<option>" + b + "</option>"
            });
            $("#languages").html(languagess_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}
function getOntology() {

    let url = $("#ontologies").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            let values_pks = result['ontologies_pk']

            ontologies_option = "<option value='all' selected>All Ontologies</option>";
            let i = 0;
            $.each(result['ontologies'], function (a, b) {
                ontologies_option += "<option value='" + values_pks[i] + "'>" + a + "</option>"
                i++;
                Object.entries(b).forEach(([k,v]) =>{
                    ontologies_option += "<option value='" + values_pks[i] + "'> &nbsp;&nbsp;&nbsp;&nbsp;" + k + "</option>"
                    i++;
                    Object.entries(v).forEach(([key,val])=>{
                        ontologies_option += "<option value='" + values_pks[i] + "'> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+ key + "</option>"
                        i++;
                    })
                })
            });



            $("#ontologies").html(ontologies_option)


        },
        error: function(response){
            console.log(response)
        }
    });
}


function add_exercise(exercise) {
    console.log("add exercise")
    var endpoint = '/resources/1/cart';
    var $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    var exercise_ids = ''
    var link = 'resources/overleaf_series/'
    var link_download = 'resources/download_series/'
    var link_download_pdf = 'resources/download_pdf/'
    $.ajax({
        url : endpoint, // the endpoint
        type : "POST", // http method
        headers:{"X-CSRFToken": $crf_token},
        data : {
          "exercise" : exercise,
        }, // data sent with the post request

        // handle a successful response
        success : function(data) {
            var updates_cart_number = String(data['exercises_number'])
            location.reload()
            $('#shopping_cart_items').text(updates_cart_number)
            exercise_ids = data['exercises_ids']
            console.log(data['exercises_ids'])
            //$("a#overleaf").prop("href", "/resource/overleaf_series/" + exercise_ids);
            console.log("success!!")
            link += exercise_ids
              link_download += exercise_ids
            link_download_pdf += exercise_ids
              console.log('link is ' + link)
              $('#overleaf').attr('href', link)
              $('#download_series').attr('href', link_download)
              $('#download_series_pdf').attr('href', link_download_pdf)
        },
       error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

    function remove_exercise(exercise) {
    var exercise_ids = ''
    var endpoint = '/resources/1/cart';
    var $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    var link = 'resources/overleaf_series/'
    var link_download = 'resources/download_series/'
    var link_download_pdf = 'resources/download_pdf/'
    $.ajax({
        url : endpoint, // the endpoint
        type : "POST", // http method
        headers:{"X-CSRFToken": $crf_token},
        data : {
          "exercise" : exercise,
          "remove" : true
        }, // data sent with the post request

        // handle a successful response
        success : function(data) {
            exercise_ids = data['exercises_ids']
            var updates_cart_number = String(data['exercises_number'])
            $('#'+exercise).remove();
            if($.trim(data['exercises_number'])) {
              $('#shopping_cart_items').text(updates_cart_number);
              link += exercise_ids
              link_download += exercise_ids
              link_download_pdf += exercise_ids
              console.log('link is ' + link)
              $('#overleaf').attr('href', link)
              $('#download_series').attr('href', link_download)
              $('#download_series_pdf').attr('href', link_download_pdf)
              console.log("success!!")
            }
            else{
              $('#shopping_cart_items').text('0')
              $('#overleaf').attr('href', '#')
              $('#download_series').attr('href', '#')
              $('#download_series_pdf').attr('href', '#');
            }
        },
       error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

    function clear_table(table_id) {
    var exercise_ids = ''
    var endpoint = '/resources/1/cart';
    var $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    var link = 'resources/overleaf_series/'
    var link_download = 'resources/download_series/'
    $.ajax({
        url : endpoint, // the endpoint
        type : "POST", // http method
        headers:{"X-CSRFToken": $crf_token},
        data : {
          "exercise" : '',
          "clear" : true
        }, // data sent with the post request

        // handle a successful response
        success : function(data) {
            $('#shopping_cart_items').text('0')
            $('#overleaf').attr('href', '#')
            $('#download_series').attr('href', '#')
            $('#download_series_pdf').attr('href', '#')
            $('#'+table_id).empty();
        },
       error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

  function getCart() {
    var endpoint = '/resources/1/cart';
    var $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    $.ajax({
        url : endpoint, // the endpoint
        type : "GET", // http method
        headers:{"X-CSRFToken": $crf_token},
        data : {

        }, // data sent with the post request

        // handle a successful response
        success : function(data) {
            console.log(data['exercises_number'])
          if(!$.trim(data['exercises_number'])){
             var updates_cart_number = '0'
            $('#shopping_cart_items').text(updates_cart_number)
          }
          else {
            var updates_cart_number = String(data['exercises_number'])
            $('#shopping_cart_items').text(updates_cart_number)
          }


        },
       error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};
function adjust_row(list_exercises) {
    var exercise_ids = ''
    var endpoint = '/resources/1/cart';
    var $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    var link = 'resources/overleaf_series/'
    var link_download = 'resources/download_series/'
    var link_download_pdf = 'resources/download_pdf/'
    $.ajax({
        url : endpoint, // the endpoint
        type : "POST", // http method
        headers:{"X-CSRFToken": $crf_token},
        data : {
          "desired_order" : list_exercises,
          "reorder" : true
        }, // data sent with the post request

        // handle a successful response
        success : function(data) {
          console.log("success")
            exercise_ids = data['exercises_ids']
            var updates_cart_number = String(data['exercises_number'])

              $('#shopping_cart_items').text(updates_cart_number);
              link += exercise_ids
              link_download += exercise_ids
              link_download_pdf += exercise_ids
              console.log('link is ' + link)
              $('#overleaf').attr('href', link)
              $('#download_series').attr('href', link_download)
              $('#download_series_pdf').attr('href', link_download_pdf)


        },
       error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

var row;
function start(){
  row = event.target;

}
function dragover() {
  var e = event;
  e.preventDefault();
  var list_exercises = ''
  let children = Array.from(e.target.parentNode.parentNode.children);
  if (children.indexOf(e.target.parentNode) > children.indexOf(row)) {
    e.target.parentNode.after(row);

    }
  else {
    e.target.parentNode.before(row);



  }
  var test3 =$('#table_id tbody tr')
  test3.each(function(){
    item_id = String(this.id) + ','
    list_exercises += item_id
  })
  console.log(list_exercises)
  adjust_row(list_exercises)
}
