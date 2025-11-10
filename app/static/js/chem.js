
//This is for the chemistry molecule
function chem_draw(hover_node,nodes)
{
    let vertices = []
    let node_index = 0

    let ids = []
    nodes.forEach(node => { ids.push(node.id)});

    node_index = ids.indexOf(hover_node);
    vertices = nodes[node_index].vertices
    vertices = vertices.toString();

    $.ajax({
        type: "POST",
        url: "/send_structure",
        data: vertices,
        dataType:'text',
        success: function (response) {
            d3.select('#chemicalSVG').selectAll('*').remove();
            response = JSON.parse(response);
            for(let i = 0; i<Object.keys(response).length-1; i++)
            {
                byteCharacters = atob(response[i]['image']);
                    byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    byteArray = new Uint8Array(byteNumbers);
                console.log(byteArray)
                var blob = new Blob([byteArray], {'type': 'image/png'});
                var url = URL.createObjectURL(blob);
                console.log(url)
                d3.select('#chemicalSVG').append('svg:image').attr("xlink:href",url).attr('x',response[i]['group']*280).attr('y',(response[i]['vertex']*275)).attr('height',250).attr('width',250)
            }
            
        },
        error: function (error) {
            console.log("error",error);
            alert("Incorrect data format!");
        }
    })
}

function send_component(a,filename)
{
    a = a.toString();
    console.log(a)
    console.log(filename)
    $.post("/send_component",{data:JSON.stringify({'name':filename,'component':a})})
}

function swap_decomposition(cur_file)
{
    that = this;
    //Let us first do stars
    console.log(cur_file);
    $.ajax({
        type: "POST",
        url: "/swap_load",
        data: cur_file,
        dataType:'text',
        success: function (response) {
            res = JSON.parse(response);
            d3.select('#graphSVG').selectAll('*').remove();
            //console.log(getEventListeners(document));
            that.graph = new Graph(res[0].mapper, res[0].col_keys, res[0].connected_components, res[0].categorical_cols, that.side_bar.other_cols,res[1]);
        },
        error: function (error) {
            console.log("error",error);
            alert("Incorrect data format!");
        }
    })
}

function reset()
{

    $.ajax({
        type: "POST",
        url: "/reset",
        data: '1',
        dataType:'text',
        success: function (response) {
            res = JSON.parse(response);
            d3.select('#graphSVG').selectAll('*').remove();
            that.graph = new Graph(res[0].mapper, res[0].col_keys, res[0].connected_components, res[0].categorical_cols, that.side_bar.other_cols,res[1]);
        },
        error: function (error) {
            console.log("error",error);
            alert("Incorrect data format!");
        }
    })

}

function geom_draw(hover_node,nodes)
{
    let vertices = []
    let node_index = 0

    let ids = []
    nodes.forEach(node => { ids.push(node.id)});

    node_index = ids.indexOf(hover_node);
    vertices = nodes[node_index].vertices
    vertices = vertices.toString();

    $.ajax({
        type: "POST",
        url: "/send_geometry",
        data: vertices,
        dataType:'text',
        success: function (response) {
            d3.select('#chemicalSVG').selectAll('*').remove();
            response = JSON.parse(response);
            for(let i = 0; i<Object.keys(response).length-1; i++)
            {
                byteCharacters = atob(response[i]['image']);
                    byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    byteArray = new Uint8Array(byteNumbers);
                console.log(byteArray)
                var blob = new Blob([byteArray], {'type': 'image/png'});
                var url = URL.createObjectURL(blob);
                console.log(url)
                d3.select('#chemicalSVG').append('svg:image').attr("xlink:href",url).attr('x',response[i]['group']*500).attr('y',(response[i]['vertex']*500)).attr('height',480).attr('width',480)
            }
            
        },
        error: function (error) {
            console.log("error",error);
            alert("Incorrect data format!");
        }
    })
}