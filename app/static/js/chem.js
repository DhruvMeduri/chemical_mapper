//This is for the chemistry molecule
function chem_draw(hover_node,nodes)
{
    let vertices = []
    let node_index = 0
    //let vert = ''

    node_index =hover_node - 1;
    vertices = nodes[node_index].vertices
    console.log("DEBUG: ",vertices)
    //vertices.push(nodes[node_index].vertices[nodes[node_index].vertices.length - 1])
    vertices = vertices.toString();

    $.ajax({
        type: "POST",
        url: "/send_structure",
        data: vertices,
        dataType:'text',
        success: function (response) {
            d3.select('#chemicalSVG').selectAll('*').remove();
            response = JSON.parse(response);
            //document.getElementById('chemical-viewer').src = 'data:;base64,' + response['image'];
            for(let i = 0; i<Object.keys(response).length-1; i++)
            {
                //let temp = 'image'.concat(i.toString())
                //console.log('CHECK: ',i)
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