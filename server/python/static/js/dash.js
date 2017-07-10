var SELECTED_HOST = null;
var STATS = {};
var DATAUPDATEID = 0;
var DEFAULT_TIMEOUT = 500;

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

function isElement(obj) {
    try {
            //Using W3 DOM2 (works for FF, Opera and Chrom)
            return obj instanceof HTMLElement;
        }
        catch(e){
            //Browsers not supporting W3 DOM2 don't have HTMLElement and
            //an exception is thrown and we end up here. Testing some
            //properties that all elements have. (works on IE7)
            return (typeof obj==="object") &&
                     (obj.nodeType===1) && (typeof obj.style === "object") &&
                     (typeof obj.ownerDocument ==="object");
                 }
}


Date.prototype.getUnixTime = function() { return this.getTime()/1000|0 };
if(!Date.now) Date.now = function() { return new Date(); }
Date.time = function() { return Date.now().getUnixTime(); }

function unixTimeToDate(timestamp) {
    return new Date(timestamp * 1000);
}

function niceTime(date) {
    // var date = new Date(Number(timestamp)*1000);
    now = new Date();

    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var minute = "0" + date.getMinutes();
    var second = "0" + date.getSeconds();
    
    if (now.getDate() == day) {
        var formattedTime = hour + ':' + minute.substr(-2);    

    } else {
        var formattedTime = month + '/' + day + '/' + hour + ':' + minute.substr(-2);    

    }
    
    return formattedTime;
}

function niceTimeDelta(date) {
    var now = new Date();
    var then = date;
    var delta = (now - then);  
    var d = new Date(delta);
    var sDelta = delta / 1000; //in s
    return niceSecondDelta(sDelta);
}

function niceSecondDelta(seconds) {

    var hrt = {};    
    hrt.days = Math.floor(seconds / 3600 / 24);
    hrt.hours = Math.floor(seconds / 3600 - 3600 * 24 * hrt.days);
    hrt.minutes = Math.floor(seconds/60 - 60 * hrt.hours);
    hrt.seconds = Math.floor(seconds - hrt.minutes * 60 - hrt.hours * 3600);

    if (hrt.minutes == 0) {
        hrt.minutes = '';
    } else {
        hrt.minutes += 'm';
    }

    if (hrt.hours == 0) {
        hrt.hours = '';
    } else {
        hrt.hours += 'h';
    }
    
    if (hrt.days == 0) {
        hrt.days = '';
    } else {
        hrt.days += 'h';
    }


    return hrt.hours + hrt.minutes  + hrt.seconds + 's';
}

function getInterval(array_of_unix_timestamps) {
    // probably no need to iterate the full data to get the interval.
    if (array_of_unix_timestamps.length >= 2) {
        return (array_of_unix_timestamps[0] - array_of_unix_timestamps[1]);
    } else {
        return DEFAULT_TIMEOUT;
    }
        
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
    if (!STATS) { return;}

    if (host == SELECTED_HOST) {
        updateGraphs(STATS[SELECTED_HOST]);
        return;
    }

    SELECTED_HOST = host;
    drawToContainer('', 'main');
    drawToContainer(SELECTED_HOST, 'hostname');
    updateGraphs(STATS[SELECTED_HOST]);
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
    // showPoint: true,
    lineSmooth: false,
    showArea: true,
    plugins: [
        Chartist.plugins.tooltip()
    ],
    axisX: {
        showGrid: false,
        
        labelInterpolationFnc: function skipLabels(value, index) {
            return index % 10  === 0 ? value : null;
        }
    },
    axisY: {
        showGrid: false
    },
};


function updateGraphs(data) {
    if (!SELECTED_HOST) { return; }

    var shortest_update = DEFAULT_TIMEOUT;

    var now = new Date();
    // HOSTS
    for (var host in STATS) {
        var id = 'id_h_' + host;
        addOrUpdateElement('hostlist', id, '<a href="" id="' + id + '" class="mdl-navigation__link" onclick=\'setCurrentHost(\"' + host + '\"); return false;\'>' + host + '</a>', host);
    }
    
    // insert all into DOM once
    for (var value in data) {
        if (value) {
            var id = value.hashCode();
            graphable = data[value][2];
            if (graphable) {
                //addOrUpdateElement('main', id, '<canvas id="' + id + '" width=100 height=100  ></canvas>', '');
                addOrUpdateElement('main', id, '<div id="' + id + '" class="ct-chart ct-perfect-fourth dataitem ' + activity + '" style="height: 100px; width:100%">' + currentDiv + '</div>', currentDiv);
            }else{
                addOrUpdateElement('main', id, '<div id="' + id + '" class="dataitem" ></div>', '');
            }
        }
    }

    // update the values
    for (var value in data) {
        if (value) {

            // TIME            
            latestTimestamp = Math.round(data[value][1][0]);
            var interval = ' ' + getInterval(data[value][1]);
            var last_seen = now.getUnixTime() - latestTimestamp;

            //ID
            var id = value.hashCode();

            var activity = 'active';
            if ((interval*1.5 - (last_seen - 5) < 0)) {activity = 'inactive';}
            
            graphable = data[value][2];

            // THIS DATA IS GRAPHABLE            
            if (graphable) {

                var humantime = [];
                var values = [];
                
                // generate some human-readable time descriptions                
                for (var entry in data[value][1]) {
                    time = unixTimeToDate(data[value][1][entry]);
                    humantime.push(niceTimeDelta(time));
                }

                for (var d in data[value][0]) {
                    values.push({ meta: 'description', value: data[value][0][d] });
                }

                currentDiv = '<b>' + value + '</b> ' + data[value][0][0] + ' ' + activity;
                addOrUpdateElement('main', id, '<div id="' + id + '" class="ct-chart ct-perfect-fourth dataitem ' + activity + '" style="height: 100px; width:100%">' + currentDiv + '</div>', currentDiv);
                //addOrUpdateElement('main', id, '<canvas id="' + id + '" class="dataitem ' + activity + '" width="400" height="100">' + currentDiv + '</div>', currentDiv);

                var ctx = document.getElementById(id);
                 
                


                 //CHARTIST CHART ////////////////////////////////////////
                 var chart = document.getElementById(id);
                 var dta = { labels: humantime, series: [values] };
                
                 if (chart) {
                     if (chart.__chartist__) {
                         chart.__chartist__.update(dta);
                     } else {
                         // WE NEED TO CREATE THE CHART
                         // console.log('init chart');
                         c = new Chartist.Line('#' + id, dta, graphOpts);
                         var testchart = document.querySelector('#' + id);
                         // console.log(testchart.__chartist__)
                     }
                 }
                 //END CHART /////////////////////////////////////////////

            // NON-GRAPHABLE DATA
            } else {
                // console.log('non-graph update');
                currentDiv = '<b>' + value + '</b>: ' + data[value][0][0] + ' ' + activity;
                addOrUpdateElement('main', id, '<div id="' + id + '" class="dataitem ' + activity + '" >' + currentDiv + '</div>', currentDiv);
            }
        } 
    }
    
}


//     return
//     // GRAPH DATA
//     for (var value in data) {
        
//        //if (! graphable) {continue;} 
//        var nicetime = [];
        
//        for (entry in data[value][1]) {
//             time = unixTimeToDate(data[value][1][entry]);
//             nicetime.push(niceTimeDelta(time));
//         }

//         var rtGraph = false;



        
//         var id = value.hashCode();
//         if (data[value][2]) {
//             var chart = document.querySelector('#' + id);
//             if (rtGraph && chart.__chartist__) {
//                 var maxsize = 60;
//                 cur_labels = chart.__chartist__.data['labels'];
//                 cur_series = chart.__chartist__.data['series'][0];

//                 cur_labels.unshift(nicetime[0]);
//                 cur_series.unshift(data[value][0][0]);                
                
//                 if (cur_labels.length > maxsize) {
//                     cur_labels.pop();
//                     cur_series.pop();
//                 }

//                 var dta = { labels: cur_labels, series: [cur_series] };
//             } else {
//                 var dta = { labels: nicetime, series: [data[value][0]] };
//             }
//             if (chart) {
//                 // UPDATE THE CHART
//                 if (chart.__chartist__) {
//                     chart.__chartist__.update(dta)
//                     //console.log('upd chart');
//                 } else {
//                     // WE NEED TO CREATE THE CHART
//                     //console.log('init chart');
//                     new Chartist.Line('#' + id, dta, graphOpts);
//                 }
//             }
//         }
//     }
//     // END GRAPHS
// }


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
    var ms = Number(interval) * 300;
    clearInterval(DATAUPDATEID);
    DATAUPDATEID = setInterval(function(){ fetch_data()}, ms);
    document.getElementById('interval').innerHTML = Math.round(ms/1000*10)/10 + 's';
}


function main() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/dump');
    xhr.onload = function() {
        data = JSON.parse(xhr.responseText);
        STATS = data;
        var hosts = Object.keys(STATS);
        if (hosts.length > 0) {SELECTED_HOST=hosts[0];}
        //console.log(SELECTED_HOST);
        //setCurrentHost(HOST);
        drawToContainer('', 'main');
        drawToContainer('', 'hostlist');
        drawToContainer(SELECTED_HOST, 'hostname');
 
        if (STATS) { updateGraphs(STATS[SELECTED_HOST]); }
        
        setInterval(function(){ updateGraphs(STATS[SELECTED_HOST])}, 150);
        setInterval(function () { get_all_stats()}, 10000);
        DATAUPDATEID = setInterval(function(){ fetch_data()}, 3000);

    };
    xhr.send();

}


main();



