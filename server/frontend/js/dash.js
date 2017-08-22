const ENDPOINT = '/dump';



Array.prototype.scaleBetween = function (scaledMin, scaledMax) {
    var max = Math.max.apply(Math, this);
    var min = Math.min.apply(Math, this);
    // console.log('MAP', this.map(num => (scaledMax-scaledMin)*(num-min)/(max-min)+scaledMin));
    
    
    // return this.map(num => (scaledMax - scaledMin) * (num - min) / (max - min + 0.0000001) + scaledMin);
    return this.map(function (num) {
        return ((scaledMax - scaledMin) * (num - min) / (max - min + 0.0000001) + scaledMin);
    })
}

Array.prototype.average = function() {
    var combined = 0;

    var length = 0;
    for (var i in this) {
        if (this.hasOwnProperty(i)) {
            combined += this[i];
            length++;
        }
    }

   
    return this.map(function () {
        return combined / length;
    });
}

Array.prototype.toFloat = function () {
    
    // return this.map(num => parseFloat(num));

    return this.map(function (num) {
        return parseFloat(num);
    })
}


// Date.prototype.getUnixTime = function() { return this.getTime()/1000|0 };
function strToLatlong(inputString) {
    // console.log('examine', inputString);
    var split = inputString.split(',');
    var long = split[1];
    var lat = split[0];
                    
    return {
        lat: lat,
        long: long
    }
}

function isURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
  '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|'+ // domain name
  '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
  '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
  '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
  '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return pattern.test(str);
}

function detectInterval(timeseries) {
    var cumulatedTime = 0;
    
    for (var i = 0; i < timeseries.length-1; i++) {
        cumulatedTime += timeseries[i] - timeseries[i+1];
    }
    
    var avgTime = cumulatedTime / timeseries.length;
    return avgTime;
}


function unixTimeToDate(timestamp) {
    return new Date(timestamp * 1000);
}

function niceTime(date) {
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

function niceTimeDelta(then) {
    var now = new Date();
    var delta = (now - then);  
    var sDelta = delta / 1000; //in s
    return niceSecondDelta(sDelta);
}

function niceSecondDelta(seconds) {

    var displaystring = '';
    var hrt = {};

    hrt.days = { value: Math.floor(seconds / 3600 / 24), label: 'd'};
    hrt.hours = { value: Math.floor(seconds / 3600 - 24 * hrt.days.value), label: 'h'};
    hrt.minutes = { value: Math.floor(seconds / 60 - 60 * hrt.hours.value - 24 * hrt.days.value * 60), label: 'm'};
    hrt.seconds = { value: Math.floor(seconds - hrt.minutes.value * 60 - hrt.hours.value * 3600 - hrt.days.value * 24 * 3600), label: 's'};

    for (i in hrt) {
        // leave out empty values
        if (hrt[i].value != 0) {
            //cull date data
            if (hrt[i].label == 'd') {hrt.seconds.value = 0};
            if (hrt[i].label == 'd') {hrt.minutes.value = 0};
            if (hrt[i].label == 'h') {hrt.seconds.value = 0};

            displaystring += (hrt[i].value + hrt[i].label);
        }
    }

    return displaystring;
}

function fit(s, low1, high1, low2, high2) {
    return low2 + (s-low1)*(high2-low2)/(high1-low1);
}



function stringToType(s, hint) {
    
    var type = 'string';
    var value = s

    if (+s === +s) {
        value = parseFloat(s);
        type = 'number';
    } else if (hint == 'location') {
        type = 'location';
        
    }
    return {
        type: type,
        value: value
    }
}




var app = new Vue({
    el: '#vue',
    data: {
        config: {
            graphAverage: false,
            graphTrend: false,
            server: ''
        },
        ready: true,
        hosts: [],
        currentHost: {},
        currentHostName: "",
        completeDB: {},
        currentDB: {},
        updateid: 1,
        server: '',
        options_visible: false,
        disconnected: true,
        currentMap: undefined,
        graphAverage: false,
        graphTrend: false
    },
    directives: {


        graph: function(canvasElement, binding) {
            // Get canvas context
            var ctx = canvasElement.getContext("2d");
            //console.log(ctx);

            
            if (ctx.canvas.clientWidth != 0) {
                ctx.canvas.width = ctx.canvas.clientWidth*1.6;
            }
            if (ctx.canvas.clientHeight != 0) {
                ctx.canvas.height = ctx.canvas.clientHeight*1.6;
            }
            var res = {
            	x: ctx.canvas.width,
            	y: ctx.canvas.height
            }
            
            var fontsize = {
                default: ctx.canvas.height/10
            }
            
            var margins = {
                bottom: ctx.canvas.height/8,
                top: ctx.canvas.height/4,
                left: ctx.canvas.width/64,
                right: ctx.canvas.width/64,
            }

            var points = binding.value[0].toFloat()

              

            var labels = binding.value[1];


            // GRAPH
            function drawChart(pts, lbls, color, do_fill) {


                //pre-calculate scaled points for display
                var pointY = pts.scaleBetween(res.y-margins.bottom-margins.top/2, margins.top)
                var pointX = [...Array(pts.length).keys()].scaleBetween(margins.left, res.x-margins.right);

                function labelExtremes(originalPoints, transformedPoints, context, color) {
                    // Draw value labels on the curve on minima/maxima
                    var lastPoint;

                    var bounds = {
                        min: Math.min(...originalPoints),
                        max: Math.max(...originalPoints)
                    };  

                    for (var op in originalPoints) {
                        // is lowest or highest value?
                        if (originalPoints.hasOwnProperty(op)) {
                            // console.log(op);
                        
//
                            if (op == 0 || (originalPoints[op] == bounds.max || originalPoints[op] == bounds.min)) {
                                if (originalPoints[op] != lastPoint) {
                                    context.fillStyle = color;
                                    context.font = fontsize.default + "px Arial";
                                    context.save();
                                    context.translate(pointX[op], transformedPoints[op] * 0.95);
                                    context.rotate(-Math.PI / 4);
                                    context.fillText(Math.round(originalPoints[op] * 10) / 10, 0, 0);
                                    context.restore();
                                    lastPoint = originalPoints[op];
                                }
                            }
                        }
                    }
                }

                ctx.beginPath();
                if (do_fill) {
                    ctx.moveTo(margins.left, res.y-margins.bottom);
                } else {
                    ctx.moveTo(margins.left, pointY[0]);
                }

                for (var op = 0; op < pts.length; op++) {
                    ctx.lineTo(pointX[op], pointY[op]);
                }
                
                if (do_fill) {
                    ctx.lineTo(res.x-margins.right, res.y-margins.bottom);
                    ctx.closePath();
                    ctx.fillStyle = color;
                    ctx.fill();
                } else {
                    ctx.stroke();
                }

                // overlay average
                /* The reason we do not reuse the graph and do it outside is the fact that
                we auto-scale the graph each frame based on it's values.*/
                if (app.config.graphAverage) {
                    console.log('draw avg');
                    var avgColor = '#222255'
                    var avgPointY = pointY.average();
                    var avgValue = pts.average();
                    ctx.beginPath();
                    ctx.moveTo(margins.left, avgPointY[0]);
                    for (var op = 0; op < pts.length; op++) {
                        ctx.lineTo(pointX[op], avgPointY[op]);
                    }
                    ctx.strokeStyle = avgColor;
                    ctx.stroke();
                    labelExtremes(avgValue, avgPointY, ctx, avgColor    );
                }

                // if (app.graphTrend) {
                //     var trendPointY = regression(pointX, pointY)[0];
                //     console.log(trendPointY);

                //     ctx.beginPath();
                //     ctx.moveTo(margins.left, trendPointY[0]);
                //     for (var i = 0; i < pts.length; i++) {
                //         ctx.lineTo(pointX[i], trendPointY[i]);
                //     }
                //     ctx.strokeStyle="#FF0000";
                //     ctx.stroke();
                //     labelExtremes(trendPointY, ctx, "#FF0000");
                // }

                

                labelExtremes(pts, pointY, ctx, "#222222");

                var nth = 0;

                var reducer = Math.round(fit(pts.length, 0, 80, 1, 10));
                //console.log(reducer);
                for (var op = 0; op < pts.length; op++) {
                    
                    if (nth == reducer || op==0) {
                        nth = 0

                        //vertical bars
                        ctx.fillStyle = "#cccccc";
                        ctx.fillRect(pointX[op], res.y-margins.bottom, 1, margins.bottom+-(res.y-pointY[op]));
                        
                        //label
                        ctx.fillStyle = "#888888";
                        ctx.fillText(lbls[op], pointX[op], res.y);
                    }
                    nth ++;
                }

            }


            drawChart(points, labels, "rgba(63,81,181,0.5)", true);

        },
    


        location: function (canvasElement, binding) {

            var pos = strToLatlong(binding.value[0]);
            var lonlat = new OpenLayers.LonLat(pos.long, pos.lat).transform('EPSG:4326', 'EPSG:3857');
            var layer = new OpenLayers.Layer.OSM();

      

            if ( app.currentMap == undefined) {
                canvasElement.innerHTML = '';
                app.currentMap = new OpenLayers.Map( {
                    projection: 'EPSG:3857',
                    layers: [
                        layer
                    ],
                    // center: new OpenLayers.LonLat(pos.long, pos.lat).transform('EPSG:4326', 'EPSG:3857'),
                    center: lonlat,
                    zoom: 16
                });

            } else {
                app.currentMap.center = lonlat;

            }
            app.currentMap.render(canvasElement.id);

      
        },

        misc: function (canvasElement, binding) {
            canvasElement.innerHTML = binding.value[0][0] + " (" + binding.value[1][0] + " ago)";
        }


    },


    computed: {
    },

    watch: {
        server: function () {
            // console.log('server changed');
            if (isURL(this.server)) {
                initApp();
                if (typeof (Storage) !== "undefined") {
                    localStorage.server = this.server;
                    console.log('Written server to local storage')
                }
            }
        },
        config: {
            handler() {
                if (typeof (Storage) !== "undefined") {
                    localStorage.config = this.config;
                    console.log('Written config')
                }   
            },
            deep: true

        }
    },

    mounted() {
        console.log('mount done');
    },

    methods: {
    
        getType: function (values, name) {
            return stringToType(values[0], name);
        },
        

        getInterval: function (timeseries) {
            return detectInterval(timeseries)
        },

        isOffline: function(timeseries) {
            const threshold = 1.8;
            var timeSinceLastUpdate = new Date().getTime() / 1000 - timeseries[0];
            if (detectInterval(timeseries) * threshold < timeSinceLastUpdate) {
                return true;
            }
            return false;
        },

        beautyfulTime: function(timeseries) {
            var newTime = [];
            for (var i = 0; i < timeseries.length; i++) {
                var time = unixTimeToDate(timeseries[i]);
                newTime.push(niceTimeDelta(time));
            }
            return newTime;
        },


  }

});








function get_all_stats() {

    if (!isURL(app.server)) {
        return;
    }

    var xhr = new XMLHttpRequest();

    xhr.onprogress = function () {
        // console.log('LOADING', xhr.status);
        if (xhr.status != '200') {
            app.disconnected = true;
        }
    }

    xhr.onload = function() {
        // console.log('onload', xhr.status);
        
        var data = {};
        try {
            data = JSON.parse(xhr.responseText);
            app.disconnected = false;
        } catch(e){
            console.log('could not parse JSON');
            app.disconnected = true;
        }
        app.completeDB = data;

        // first run: set hostname
        if (app.currentHostName == "") {
            app.currentHostName = Object.keys(app.completeDB)[0];
        }

        // trigger refresh of currently active host
        app.currentHost = app.completeDB[app.currentHostName];
        
    };

    xhr.open('GET', app.server + ENDPOINT, true);
    
    try {
        xhr.send();
        // app.disconnected = false;
        
    } catch(e) {
        console.log('err');
        app.disconnected = true;
        
    }
}

// function changeInterval(interval) {
//     var ms = Number(interval) * 300;
//     clearInterval(DATAUPDATEID);
//     DATAUPDATEID = setInterval(function(){ fetch_data()}, ms);
//     document.getElementById('interval').innerHTML = Math.round(ms/1000*10)/10 + 's';
// }

function initApp() {
    get_all_stats();
    // app.currentHostName = Object.keys(app.completeDB)[0];

    // trigger refresh of currently active host
    // app.currentHost = app.completeDB[app.currentHostName];
    

}


function main() {
    
    var savedServer = localStorage.server;
    if (savedServer !== "undefined") {
        app.server = savedServer;
    } else {
        console.log('could not restore server')
    }
    
    if (localStorage.config !== "undefined") {
        // app.config = localStorage.config;
        console.log(localStorage.config);
    }

    initApp();
    // console.log(app.currentHostName);
    // console.log(app.currentHost);

    setInterval(function () { get_all_stats()}, 350);

    /*
    var xhr = new XMLHttpRequest();
    // xhr.open('GET', 'http://localhost:4000/dump');
    xhr.open('GET', app.server);
    xhr.onload = function() {
        data = JSON.parse(xhr.responseText);
        app.completeDB = data;
        // on first launch, pick one of the hosts so that the list is not empty
        app.currentHostName = Object.keys(app.completeDB)[0];
        app.currentHost = app.completeDB[app.currentHostName];

        // setInterval(function(){ updateGraphs(STATS[SELECTED_HOST])}, 150);
        
        // refresh data every x sec
        setInterval(function () { get_all_stats()}, 5000);
        
        // DATAUPDATEID = setInterval(function(){ fetch_data()}, 3000);
    };
    xhr.send();

*/
}

main();
