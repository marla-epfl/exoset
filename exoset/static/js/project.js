

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


    //$('#resources').on('change', function () {
        // since province and region is dependent

        // on country select, emty all the options from select input


        // update the selected country

        //if(this.value == "all")
           // send_data['author'] = "";
       // else
           // send_data['author'] = this.value;

        //get province of selected country

        // get api data of updated filters

        //getAPIData();
   // });

    $('#levels').on('change', function () {


        if(this.value == "all")
            send_data['level'] = "";
        else
            send_data['level'] = this.value;

        //get province of selected country

        // get api data of updated filters

        getAPIData();
    });
    $('#families').on('change', function () {


        if(this.value == "all")
            send_data['tagproblemtype'] = "";
        else
            send_data['tagproblemtype'] = this.value;

        //get province of selected country

        // get api data of updated filters

        getAPIData();
    });
    $('#courses').on('change', function () {


        if(this.value == "all")
            send_data['course'] = "";
        else
            send_data['course'] = this.value;

        //get province of selected country

        // get api data of updated filters

        getAPIData();
    });
    $('#tags').on('change', function () {


        if(this.value == "all")
            send_data['concept'] = "";
        else
            send_data['concept'] = this.value;

        //get province of selected country

        // get api data of updated filters

        getAPIData();
    });
    $('#languages').on('change', function () {


        if(this.value == "all")
            send_data['language'] = "";
        else
            send_data['language'] = this.value;

        //get province of selected country

        // get api data of updated filters

        getAPIData();
    });
    $('#ontologies').on('click', function () {


        if(this.value == "all")
            send_data['ontology'] = "";
        else
            send_data['ontology'] = this.value;

        //get province of selected country

        // get api data of updated filters

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


    //clearing up the province and region select box

    //getAuthors("all");
    //getRegion("all");

    //send_data['author'] = '';

    //send_data['format'] = 'json';
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

            row = "<tr> "  + "<td style='width: 22%' title=\"" + b.title + "\">" + b.title.slice(0, 50) + "..." + "</td>"+
                "<td style='width: 14%'>" + b.family_problem + "</td><td style='width: 13%'>" +
                b.related_courses + "</td><td style='width: 8%'>" + b.tag_level + "</td>" +
                "<td style='width: 13%'>" + b.ontology_path  + "</td>" + "<td style='width: 11%'>" +
                b.tag_concept  + "</td><td style='width: 15%'>" + b.prerequisite_assigned +
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
                levels_option += "<option>" + b + "</option>"
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
                courses_option += "<option>" + b + "</option>"
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
                tag_families_option += "<option>" + b + "</option>"
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
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#ontologies").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            ontologies_option = "<option value='all' selected>All Ontologies</option>";
            $.each(result["ontologies"], function (a, b) {
                ontologies_option += "<option>"  + a + "</option>"
                Object.entries(b).forEach(([k,v]) =>{
                    ontologies_option += "<option>" + " &nbsp;&nbsp;&nbsp;&nbsp;" + k + "</option>"
                    for (i=0; i<v.length;i++){
                        ontologies_option += "<option>" +" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+ v[i] + "</option>"
                    }
                })
            });
            $("#ontologies").html(ontologies_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}
