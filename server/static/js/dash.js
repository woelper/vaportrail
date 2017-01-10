var SELECTED_HOST = null;
var STATS = {};
var DATAUPDATEID = 0;

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
    var date = new Date(Number(timestamp)*1000);
    var hours = date.getHours();
    var minutes = "0" + date.getMinutes();
    var seconds = "0" + date.getSeconds();

    var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
    return formattedTime;
}

function niceUnixTimeDelta(timestamp) {
    var date = new Date(timestamp*1000);
    var hours = date.getHours();
    var minutes = "0" + date.getMinutes();
    var seconds = "0" + date.getSeconds();

    var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
    return formattedTime;
}

function displayOptions(_id) {

    element = document.getElementById(_id);
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

function setCurrentHost(host) {
    if (host == SELECTED_HOST) {
        if (STATS) { updateGraphs(STATS[SELECTED_HOST]); }
        return;
    }

    SELECTED_HOST = host;
    drawToContainer('', 'main');
    drawToContainer(SELECTED_HOST, 'hostname');
    if (STATS) { updateGraphs(STATS[SELECTED_HOST]); }
    //fetch_and_update(HOST);
}

function drawToContainer(data, container) {
    var target = document.getElementById(container);
    target.innerHTML = data;
}

function addOrUpdateElement(containerId, elementId, completeContent, updateContent) {
    // the 'main' div to hold divId's content
    var targetDiv = document.getElementById(containerId);
    var oldElement = document.getElementById(elementId);
    if (oldElement) {
        //UPDATE
        if (updateContent != oldElement.innerHTML) {
            oldElement.innerHTML = updateContent;
        }
    }
    else {
        // the element is added, since it does not exist
        targetDiv.innerHTML += completeContent;
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
            return index % 5  === 0 ? value : null;
        }
    },
    axisY: {
        showGrid: false
    },
};


function updateGraphs(data) {
    if (!SELECTED_HOST) { return; }

    // HOSTS
    for (var host in STATS) {
        id = 'id_h_' + host;
        addOrUpdateElement('hostlist', id, '<a href="" id="' + id + '" class="mdl-navigation__link" onclick=\'setCurrentHost(\"' + host + '\"); return false;\'>' + host + '</a>', host);
    }
    
    
       
    for (var value in data) {
        if (value) {
            var id = value.hashCode();
            graphable = data[value][2];
            if (graphable) {
                currentDiv = '<b>' + value + '</b> ' + data[value][0][0];
                addOrUpdateElement('main', id, '<div id="' + id + '" class="ct-chart ct-perfect-fourth dataitem" style="height: 100px; width:100%">'+currentDiv+'</div>', currentDiv);

            } else {
                currentDiv = '<b>' + value + '</b>: ' + data[value][0][0];
                addOrUpdateElement('main', id, '<div id="' + id + '" class="dataitem" >' + currentDiv + '</div>', currentDiv);
            }
        }
    }

    // GRAPHS    
    for (var value in data) {
        
       //if (! graphable) {continue;} 
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
                    //console.log('upd chart');
                } else {
                    // WE NEED TO CREATE THE CHART
                    //console.log('init chart');
                    new Chartist.Line('#' + id, dta, graphOpts);
                }
            }
        }
    }
    // END GRAPHS
}


function get_all_stats() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/dump');
    xhr.onload = function() {
        data = JSON.parse(xhr.responseText);
        STATS = data;
    };
    xhr.send();
}


function fetch_data() {
    if (!SELECTED_HOST) { return; }
    var xhr = new XMLHttpRequest();
    //xhr.open('GET', '/dump');
    xhr.open('GET', '/dump?host=' + SELECTED_HOST);
    xhr.onload = function() {
        var data = JSON.parse(xhr.responseText);
        //STATS = data;
        STATS[SELECTED_HOST] = data;
    };
    xhr.send();
}

function changeInterval(interval) {
    var ms = Number(interval) * 400;
    clearInterval(DATAUPDATEID);
    DATAUPDATEID = setInterval(function(){ fetch_data()}, ms);
    console.log(ms);
}


function main() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/dump');
    xhr.onload = function() {
        data = JSON.parse(xhr.responseText);
        STATS = data;
        var hosts = Object.keys(STATS);
        if (hosts.length > 0) {SELECTED_HOST=hosts[0];}
        console.log(SELECTED_HOST);
        //setCurrentHost(HOST);
        drawToContainer('', 'main');
        drawToContainer('', 'hostlist');
        drawToContainer(SELECTED_HOST, 'hostname');
 
        if (STATS) { updateGraphs(STATS[SELECTED_HOST]); }
        //updateGraphs(STATS[HOST]);
        setInterval(function(){ updateGraphs(STATS[SELECTED_HOST])}, 200);
        setInterval(function () { get_all_stats()}, 10000);
        DATAUPDATEID = setInterval(function(){ fetch_data()}, 10000);

    };
    xhr.send();

}


main();



