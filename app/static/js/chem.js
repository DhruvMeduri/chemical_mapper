//This is for the chemistry molecule
function chem_draw(hover_node,nodes)
{
    let vertices = []
    let node_index = 0
    //let vert = ''

    node_index =hover_node - 1;
    vertices.push(nodes[node_index].vertices[0])
    vertices.push(nodes[node_index].vertices[nodes[node_index].vertices.length - 1])
    vertices = vertices.toString();

    $.ajax({
        type: "POST",
        url: "/send_structure",
        data: vertices,
        dataType:'text',
        success: function (response) {
            response = JSON.parse(response);
            //document.getElementById('chemical-viewer').src = 'data:;base64,' + response['image'];
            console.log(response)
            byteCharacters = atob(response['image1']);
                byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                byteArray = new Uint8Array(byteNumbers);
            console.log(byteArray)
            var blob = new Blob([byteArray], {'type': 'image/png'});
            var url = URL.createObjectURL(blob);
            console.log(url)
            d3.select('#chemicalSVG').append('svg:image').attr("xlink:href",url).attr('x',100).attr('height',180)

            byteCharacters = atob(response['image2']);
                    byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                    byteArray = new Uint8Array(byteNumbers);
            console.log(byteArray)
            var blob = new Blob([byteArray], {'type': 'image/png'});
            url = URL.createObjectURL(blob);
            console.log(url)
            d3.select('#chemicalSVG').append('svg:image').attr("xlink:href",url).attr('x',500).attr('height',180)

            
        },
        error: function (error) {
            console.log("error",error);
            alert("Incorrect data format!");
        }
    })
}