var HOST = null;

String.prototype.hashCode = function() {
  var hash = 0, i, chr, len;
  if (this.length === 0) return 'id' + hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return 'id' + hash;
};

function setCurrentHost(host) {
    HOST = host;
    drawToContainer('', 'main');
    fetch_and_update(HOST);
}

function drawToContainer(data, container) {
    var target = document.getElementById(container);
    target.innerHTML = data;
}

function addOrUpdateDiv(targetId, divId, content, _class, _style) {
    // the 'main' div to hold divId's content
    var targetDiv = document.getElementById(targetId);
    var currentDiv = document.getElementById(divId);
    if (currentDiv) {
        if (content != currentDiv.innerHTML) {
            currentDiv.innerHTML = content;
        }
    }
    else {
        targetDiv.innerHTML += '<div id=' + divId + ' class="' + _class + '" style="' + _style +'" >' + content + '</div>'
    }
}

function addOrUpdateGraph (container, div) { 
    var newDiv = document.createElement("div"); 
    var newContent = document.createTextNode(text); 
    newDiv.appendChild(newContent); //add the text node to the newly created div. 
    var currentDiv = document.getElementById(container); 
    document.body.insertBefore(newDiv, currentDiv); 
}

graphOpts = {
    showPoint: false,
    lineSmooth: false,
    showArea: true,
    axisX: {
        showGrid: false,
        
        labelInterpolationFnc: function skipLabels(value, index) {
            return index % 10/5  === 0 ? value : null;
        }
    },
    axisY: {
        showGrid: false
    },
};


function updateData(data) {

    for (var value in data) {
        if (value) {
            var id = value.hashCode();
            graphable = data[value][2];
            if (graphable) {
                currentDiv = value;
                addOrUpdateDiv('main', id, currentDiv, "ct-chart ct-perfect-fourth dataitem", "height: 100px; width:100%");

            } else {
                currentDiv = value + ': ' + data[value][0][0];
                addOrUpdateDiv('main', id, currentDiv, "dataitem", "");
            }
        }
    }

    // GRAPHS    
    for (var value in data) {
        var id = value.hashCode();
        if (data[value][2]) {
            var dta = { labels: data[value][1], series: [data[value][0]] };
            var chart = document.querySelector('#' + id);
            if (chart) {
                // UPDATE THE CHART
                if (chart.__chartist__) {
                    chart.__chartist__.update(dta)
                } else {
                    // WE NEED TO CREATE THE CHART
                    new Chartist.Line('#' + id, dta, graphOpts);
                }
            }
        }
    }
    // END GRAPHS
}


function get_hosts() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/dump');
    xhr.onload = function() {
        data = JSON.parse(xhr.responseText);
        var hoststring = '';
        var lasthost = null;
        for (var host in data) {
            lasthost = host;
            hoststring += '<a href="" class=\"mdl-navigation__link\" onclick=\'setCurrentHost(\"' + host + '\"); return false;\'>' + host +'</a>'
        }
        drawToContainer(hoststring, 'hostlist');
        
        if (lasthost) {
            setCurrentHost(lasthost);
        }
    };
    xhr.send();
}


function fetch_and_update(host) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/dump?host=' + host);
    
    xhr.onload = function() {
        var data = JSON.parse(xhr.responseText);
        updateData(data);
    };
    xhr.send();
}


function update_data() {
    if (HOST) {
        fetch_and_update(HOST);
    }
}


get_hosts();

var intervalID = setInterval(function(){ update_data() }, 500);

