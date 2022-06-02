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
    document.getElementById("article_details").style.visibility = 'visible';
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
    bloc.innerHTML =`${bloc.innerHTML}  <div id="${id}" style='width:90%; background-color:yellow; display:flex; flex-wrap: wrap; margin:10px;' onclick="select_filter('${id}')"> ${close_button} </div> `;

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
        let name = args[0];
        post_data = `Type:author;name:${name}`;
        post_data = escapeHtml(post_data);
        
        //data to display
        display_data = `Author: ${name} `
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

    else if(type=="doi")
    {
        //data to send
        let doi_article = args[0];
        post_data=`Type:neighbour;DOI:${doi_article};`;
        post_data = escapeHtml(post_data);

        //data to display
        display_data = `DOI: ${doi_article}`;
        display_data = escapeHtml(display_data);
    }

    else
    {
        
        return "";
    }

    // the data hidden used by a POST request when the button generate is used
    let html_input_code = `<input id='${id_input_html}' type='text' name='${name_input}' value='${post_data}' hidden>`;
    document.getElementById("data_filter").innerHTML += html_input_code;

    // the data display in web page
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

//check, uncheck all
function toggle(source) {
    checkboxes = document.getElementsByName('check_row');
    for(var i=0, n=checkboxes.length;i<n;i++) {
      checkboxes[i].checked = source.checked;
    }
  }


let current_type_filter = {"type":"Topic","id_input":"topic_input"}

// when we change the type of filter
function change_type_filter()
{
    
    //we get the value of the selection
    let type = document.getElementById("type_filter").value;
    let id_input = "";

    if (type == "Topic")
    {
        id_input="topic_input";
        
    }
    else if (type == "Author")
    {
        id_input="author_input";
       
    }
    else if (type == "Keyword")
    {
        id_input="keyword_input";
        
    }
    else if (type == "DOI")
    {
        id_input="doi_input";
        
    }
    else
    {
        return false;
    }

    //we hide current input 
    document.getElementById(current_type_filter.id_input).style.visibility = "hidden";

    //we display new input 
    document.getElementById(id_input).style.visibility = "visible";

    //we save the current type data
    current_type_filter.type = type;
    current_type_filter.id_input = id_input;

}

function add_topic()
{
    topic_value = document.getElementById("topic_input_value").value
    add_data_post("topic", topic_value)
}

function add_author()
{
    author_name = document.getElementById("author_input_value").value
    add_data_post("author", author_name)
}

function add_keyword()
{
    keyword = document.getElementById("keyword_input_value").value
    add_data_post("keyword",keyword)
}

function add_doi()
{
    doi = document.getElementById("doi_input_value").value
    add_data_post("doi",doi)
}