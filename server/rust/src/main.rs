#![feature(plugin)]
#![plugin(rocket_codegen)]

extern crate rocket;
#[macro_use]
extern crate lazy_static;
extern crate time;

use rocket::Outcome;
use rocket::request::{self, FormItems, FromRequest};
use rocket::http::Status;
use std::collections::HashMap;
use rocket::Request;
use std::sync::RwLock;


#[derive(Debug)]
enum EntryValue {
    EntryString(String),
    EntryFloat(f64),
    EntryInt(i64)
}

#[derive(Debug)]
struct Entry {
    // val: EntryValue,
    val: String,
    timestamp: i64
}

type EntryLog = Vec<Entry>;
type Data = HashMap<String, EntryLog>;
type HostInfo = String;


lazy_static! {
    static ref DB: RwLock<HashMap<HostInfo, Data>> = RwLock::new(HashMap::new());
}


pub struct MyHostStuff {
    // db: Option<HashMap<String, String>>
    items: String
}

impl <'a, 'r> FromRequest<'a, 'r> for MyHostStuff {
    type Error = &'static str;
    fn from_request(req: &'a Request<'r>) -> request::Outcome<Self, Self::Error> {

        match req.uri().query() {
            Some(query) => {

                Outcome::Success(MyHostStuff {
                    items: query.to_string()
                })

            },
            None => Outcome::Failure((Status::BadRequest, "noep" ))
        }
    }
}


#[get("/")]
pub fn add(my_host_stuff: MyHostStuff) -> &'static str {

    let id = "host";
    let mut db = DB.write().unwrap();
    // println!("DB {:?}", db);
    
    let mut host = false;
    let mut web_params = HashMap::new();
 
    // let mut kvdata = Data::new();
    let mut hostname = "";

    println!("my_host_stuff.items {}", &my_host_stuff.items);        
    
    //the only convention we have: we have to have an id currently called 'host'
    // let mut url = "sdsdssdsdsd";
    let url = my_host_stuff.items.as_str();

    for (key, value) in FormItems::from(url) {
        if key == id {
            println!("Host is {}", value);        
            host = true;
            hostname = value;
        }
        else {
            // println!("will insert {} : {}", key, value);
            // db.insert(key.to_string(), value.to_string());
            web_params.insert(key.to_string(), value.to_string());            
        }
    }

    // bail out if no host is set
    if host != true { return "No Host in your query. Please specify /add?host=hostname&value=some_value."; }


    println!("last kvdata {:?}", web_params);
    // insert only new items
    if db.contains_key(&hostname.to_string()) {
        println!("Updating: {:?}", hostname);

        if let Some(vals) = db.get_mut(&hostname.to_string()) {
            println!("prev vals {:?}", vals);

        }
        // assert_eq!(db["host"], "b");

        // let values = db.entry(hostname.to_string());
        // println!("hdb {:?}", values.entry("host"));
        
        // match db. {
        //     Some(expr) => expr,
        //     None => expr,
        // }
        // println!("hdb {:?}", hdb);
        
        // for (hkey, hvalue) in &hdb {
        //     println!("{:?}, {:?}", hkey, hvalue);
            
        // }


        // let mut val: EntryValue;
        // val = EntryValue(1);
        let mut entry = Entry {
            val: "ds".to_string(),
            timestamp: time::get_time().nsec as i64
            };
        entry.val = "1".to_string();
        // entry.timestamp = time::precise_time_s();

        let mut entry_log = EntryLog::new();
        entry_log.push(entry);
        
        let mut data = Data::new();
        data.insert("sdsdsd".to_string(), entry_log);


        db.insert(hostname.to_string(), data);
        println!("global db {:?}", *db);
        return "host updated";
        
    } else {

        let mut data = Data::new();

        for (key, value) in web_params {
            
            println!("k={} v={}", key, value);
            let mut entry_log = EntryLog::new();
            let entry = Entry {val: value.to_string(), timestamp: time::get_time().nsec as i64};
            entry_log.push(entry);
            data.insert(key.to_string(), entry_log);
        }


        db.insert(hostname.to_string(), data);

        return "No host by this name, adding.";
    
    }

    
}




fn main() {

    {let _ = DB.read().unwrap();}
    //rocket::ignite().catch(errors![not_found]).launch();
    rocket::ignite().mount("/add", routes![add]).launch();

}