    Vue.component('stringvalue', {
  // declare the props
  props: ['values'],
  template: '<b>{{ values }}</b>'
})

var app = new Vue({
    el: '#vue',
    data: {
        ready: true,
        hosts: [],
        currentHost: {},
        currentHostName: "",
        completeDB: {},
        currentDB: {},
        updateid: 1,
        server: '',
        options_visible: false,
        disconnected: true
    },
    computed: {
    },

    watch: {
        // whenever question changes, this function will run
        server: function () {
            // console.log('server changed');
            if (isURL(this.server)) {
                initApp();
                if (typeof(Storage) !== "undefined") {
                    localStorage.server = this.server;
                    console.log('written server to local strg')
                }
            }
        }
    },

    mounted() {
        console.log('mount done');
    },

    methods: {
    
        drawSVG: function () {
            return '';
        },
        
        isOffline: function (timeseries) {
            var cumulatedTime = 0;
            const threshold = 1.5;

            for (var i = 0; i < timeseries.length-1; i++) {
                cumulatedTime += timeseries[i] - timeseries[i+1];
            }
            
            var avgTime = cumulatedTime / timeseries.length;
            var timeSinceLastUpdate = new Date().getTime() / 1000 - timeseries[0];
            // console.log(avgTime, timeSinceLastUpdate);
            if (avgTime * threshold < timeSinceLastUpdate) {
                return true;
            }
            return false;
        },

        beautyfulTime: function (timeseries) {
            var newTime = [];
            for (var i = 0; i < timeseries.length; i++) {
                var time = unixTimeToDate(timeseries[i]);
                newTime.push(niceTimeDelta(time));
            }
            return newTime;
        },

        chartData: function (arr1, arr2) {
            var data = [];
            if (arr1.length != arr2.length) {return []};
            for (var i = 0; i < arr1.length; i++) {
                data.push([arr1[i], arr2[i]]);
            }        
            return data;
        },
  }

});





function isURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
  '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|'+ // domain name
  '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
  '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
  '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
  '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return pattern.test(str);
}

// Date.prototype.getUnixTime = function() { return this.getTime()/1000|0 };

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

    xhr.open('GET', app.server, true);
    
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
    
    initApp();
    // console.log(app.currentHostName);
    // console.log(app.currentHost);

    setInterval(function () { get_all_stats()}, 5000);

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
