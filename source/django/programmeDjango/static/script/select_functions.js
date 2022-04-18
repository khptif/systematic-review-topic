let id_article_shown = '0';

function escapeHtml(unsafe)
{
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }

// show the article when click on cluster
function article_show(article_id)
{
    // hide the previous article
    if(id_article_shown != '0')
    {
        document.getElementById(id_article_shown).style.visibility='hidden';
    }
    // display the article
    document.getElementById(article_id).style.visibility='visible';
    id_article_shown = article_id
    // make the scroll to top
    document.getElementById("article_details").scrollTop = 0;
}


function light(element)
{
    element.style.filter= "brightness(4000000)";
    element.style.width ="20px"
    element.style.height ="20px"
    element.style.zIndex = "1";
}

function dark(element)
{
    element.style.width ="10px"
    element.style.height ="15px"
    element.style.filter= "brightness(1)"
    element.style.zIndex = "0";
}

function light_cluster(topic)
{
    var graphic = document.getElementById("cluster_display")
    var points = graphic.getElementsByClassName(topic)
    for (let i = 0; i< points.length;i++)
    {
        light(points[i])
    }
    
}

function dark_cluster(topic)
{
    let graphic = document.getElementById("cluster_display")
    let points = graphic.getElementsByClassName("topic_"+topic)
    for (let i = 0; i< points.length;i++)
    {
        dark(points[i])
    }
    
}

var current_filter="";
var number_filter=0;

// get a new bloc of filters
function add_filter()
{
    // get the button to add filter
    let add_button = document.getElementById("add_filter").innerHTML
    // remove the button
    document.getElementById("add_filter").remove()

    // we add the filter
    let id = `filter_${number_filter}`;
    let close_function = `close_div('${id}')`;
    let close_button = `<button type="button" onclick="${close_function}" style='width:50px;height:50px; margin:10px;'> X </button>`;
    var bloc = document.getElementById("filters");
    bloc.innerHTML =`${bloc.innerHTML}  <div id="${id}" style='width:100%; background-color:yellow; display:flex; flex-wrap: wrap; margin-bottom:10px;' onclick="select_filter('${id}')"> ${close_button} </div> `;

    // we put the add button
    bloc.innerHTML += `<div id='add_filter'> ${add_button}</div>`;
    //we increment filters id
    number_filter++;
}

// get a list of id and remove the associate html element
function close_div(...id)
{
    for(let i=0;i<id.length;i++)
    {
        document.getElementById(id[i]).remove()
    }
    
}

// select the current bloc filter 
function select_filter(id)
{
    let previous_filter = current_filter
    if(previous_filter != "")
    {
        // if the previous filter has been removed, this code get error so we put a try...finally
        try{
            document.getElementById(previous_filter).style.backgroundColor = "yellow"
        }
        finally
        {
            current_filter = id
            document.getElementById(current_filter).style.backgroundColor = "magenta"
        }
    }
    current_filter = id
    document.getElementById(current_filter).style.backgroundColor = "magenta"
}

// data to send to server with POST
var number_post = 0;
var id_input = 0;
function add_data_post(type, ...args)
{
    // if no filter is selected
    if(current_filter == "")
    {
        
        return "";
    }

    // we define id for filter and input
    let name_input = `${current_filter}_${number_filter}`;
    number_filter ++;
    let id_input_html = `input_${id_input}`;
    let id_div_html = `div_${id_input}`;
    id_input ++;

    let close_function = `close_div('${id_input_html}','${id_div_html}')`;
    let button_close = `<button type='button' onclick="${close_function}" > X </button>`;
    let post_data = ""
    let display_data = ""

    // if we double click on a topic
    if(type=="topic")
    {
        //data to send
        let topic = args[0];
        post_data = `Type:topic;topic_name:${topic};`;
        post_data = escapeHtml(post_data);

        //display the data
        display_data = escapeHtml(`topic: ${topic}`);
         
    }
    // if we submit last name and first name of a author
    else if(type=="author")
    {
       
        //data to send
        let last_name = args[0];
        let first_name = args[1];
        post_data = `Type:author;last_name:${last_name};first_name:${first_name};`;
        post_data = escapeHtml(post_data);
        
        //data to display
        display_data = `Author: ${last_name} ${first_name}`
        display_data = escapeHtml(display_data)
    }

    else if(type=="keyword")
    {
        // data to send
        let keyword = args[0];
        post_data =`Type:keyword;keyword:${keyword};`;
        post_data = escapeHtml(post_data);

        //data to display
        display_data = `Keyword: ${keyword}`;
        display_data = escapeHtml(display_data);
    }

    else if(type=="neighbour")
    {
        //data to send
        let doi_article = args[0];
        post_data=`Type:neighbour;DOI:${doi_article};`;
        post_data = escapeHtml(post_data);

        //data to display
        display_data = `Neighbour: ${doi_article}`;
        display_data = escapeHtml(display_data);
    }

    else
    {
        
        return "";
    }

    let html_input_code = `<input id='${id_input_html}' type='text' name='${name_input}' value='${post_data}' hidden>`;
    document.getElementById("data_filter").innerHTML += html_input_code;

    let display_filter_html_code = `<div id="${id_div_html}" style="margin-right:5px;background-color:rgba(255,255,255,0.5)">${button_close} ${display_data} </div>`;
    document.getElementById(current_filter).innerHTML += display_filter_html_code;
}

// add an author in filter
function submit_author()
{
    let last_name = document.getElementById('last_name').value;
    let first_name = document.getElementById('first_name').value; 
    add_data_post("author",last_name,first_name);
}

//add keywords in filter
function submit_keyword()
{
    let keyword = document.getElementById('keyword_search').value;
    add_data_post("keyword",keyword)
}

//add neighbour article
function submit_neighbour()
{
    let doi_article = document.getElementById('neighbour').value;
    add_data_post("neighbour",doi_article)
}