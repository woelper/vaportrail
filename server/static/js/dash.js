var HOST = null;
var STATS = {};


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


function niceUnixTime(timestamp) {
    var date = new Date(timestamp*1000);
    var hours = date.getHours();
    var minutes = "0" + date.getMinutes();
    var seconds = "0" + date.getSeconds();

    var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
    return formattedTime;
}


function setCurrentHost(host) {
    HOST = host;
    drawToContainer('', 'main');
    drawToContainer('<h5>' + HOST + '</h5>', 'hostname');
    
    if (STATS) { updateGraphs(STATS[HOST]); }
    //fetch_and_update(HOST);
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


function updateGraphs(data) {

    

    //BLOCKED = true;

    for (var value in data) {
        if (value) {
            var id = value.hashCode();
            graphable = data[value][2];
            if (graphable) {
                currentDiv = '<b>' + value + '</b> ' + data[value][0][0];
                addOrUpdateDiv('main', id, currentDiv, "ct-chart ct-perfect-fourth dataitem", "height: 100px; width:100%");

            } else {
                currentDiv = '<b>' + value + '</b>: ' + data[value][0][0];
                addOrUpdateDiv('main', id, currentDiv, "dataitem", "");
            }
        }
    }

    // GRAPHS    
    for (var value in data) {
        
        var nicetime = [];
        
        for (entry in data[value][1]) {
            nicetime.push( niceUnixTime(data[value][1][entry]) );
        }

        var id = value.hashCode();
        if (data[value][2]) {
            var dta = { labels: nicetime, series: [data[value][0]] };
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
    //BLOCKED = false;
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
        
        // set current host if unset
        if (! HOST) {
            if (lasthost) {
                setCurrentHost(lasthost);
            }
        }

        // make sure we have an initial dataset        
        fetch_data();

    };
    xhr.send();
}


function fetch_and_update() {
    if (! HOST) { return }
    
    //console.log(STATS);

    // var xhr = new XMLHttpRequest();
    // xhr.open('GET', '/dump?host=' + HOST);
    
    // xhr.onload = function() {
    //     var data = JSON.parse(xhr.responseText);
    //     updateGraphs(data);
    // };
    // xhr.send();

    if (STATS) {
        updateGraphs(STATS[HOST]);
    }

}

function fetch_data() {

    if (! HOST) { return }

    
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/dump');
    //xhr.open('GET', '/dump?host=' + HOST);

    
    xhr.onload = function() {
        var data = JSON.parse(xhr.responseText);
        //updateGraphs(data);
        STATS = data;
    };
    xhr.send();
}




get_hosts();

var intervalID = setInterval(function(){ fetch_and_update() }, 500);
// hosts need a lower update interval
var intervalID = setInterval(function () { get_hosts() }, 10000);

var intervalID = setInterval(function(){ fetch_data() }, 1000);



