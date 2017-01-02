

function addElement (text, container) { 
  // create a new div element 
  // and give it some content 
  var newDiv = document.createElement("div"); 
  var newContent = document.createTextNode(text); 
  newDiv.appendChild(newContent); //add the text node to the newly created div. 

  // add the newly created element and its content into the DOM 
  var currentDiv = document.getElementById(container); 
  document.body.insertBefore(newDiv, currentDiv); 
}



function renderData(data) {
    //console.log(data);
    for (var key in data) {
        if (data.hasOwnProperty(key)) {
            console.log(key + " -> " + data[key]);
            addElement(key, main);
            for (var val in data[key]) {
                addElement(val, stats);
        }
    }

}


var xhr = new XMLHttpRequest();
xhr.open('GET', '/dump');
xhr.onload = function() {
    
    data = {};
    data = JSON.parse(xhr.responseText);
    renderData(data);
    
    // if (xhr.status === 200) {
    //     data = JSON.parse(xhr.responseText);
    //     renderData(data);;
    // }
    // else {
    //     alert('Request failed.  Returned status of ' + xhr.status);
    // }

};
xhr.send();



// new Vue({
//   el: '#hosts',
//   data: {
//     message: 'a'
//   }
// })



