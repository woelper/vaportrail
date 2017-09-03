#![feature(plugin)]
#![plugin(rocket_codegen)]

extern crate rocket;
extern crate serde_json;
#[macro_use] extern crate rocket_contrib;
#[macro_use] extern crate serde_derive;
#[macro_use] extern crate lazy_static;
extern crate time;


use std::collections::HashMap;
use rocket::Outcome;
use rocket::request::{self, FormItems, FromRequest};
use rocket::http::Status;
use rocket::Request;
use std::sync::RwLock;


#[derive(Debug, Deserialize, Serialize)]
struct Entry {
    val: String,
    timestamp: i64
}

type EntryLog = Vec<Entry>;
type Data = HashMap<String, EntryLog>;
type HostInfo = String;


lazy_static! {
    static ref DB: RwLock<HashMap<HostInfo, Data>> = RwLock::new(HashMap::new());
    // static ref DB: <HashMap<HostInfo, Data>> :: HashMap::new();
    
}


pub struct URLArgs {
    items: String
}

impl <'a, 'r> FromRequest<'a, 'r> for URLArgs {
    type Error = &'static str;
    fn from_request(req: &'a Request<'r>) -> request::Outcome<Self, Self::Error> {

        match req.uri().query() {
            Some(query) => {

                Outcome::Success(URLArgs {
                    items: query.to_string()
                })
            },
            None => Outcome::Failure((Status::BadRequest, "noep" ))
        }
    }
}




// #[get("/dump", format = "application/json")]
#[get("/dump")]
pub fn dump() -> &'static str {
    let mut db = DB.read().unwrap();
    // let mut a = *db.Debug();
    // let response = *db.to_string();
    // let mut data = &db.get_mut(dataname);
    println!("{:?}", *db);
    return "";
}

#[get("/add")]
pub fn add(args: URLArgs) -> &'static str {

    // how we group values together
    let id_name = "host";

    //open DB for writing
    let mut db = DB.write().unwrap();
    
    let mut host = false;
    let mut arg_dict = HashMap::new();
 
    let mut hostname = "";

    println!("args.items {}", &args.items);        
    
    let url = args.items.as_str();

    for (key, value) in FormItems::from(url) {
        if key == id_name {
            println!("Host is {}", value);        
            host = true;
            hostname = value;
        }
        else {
            arg_dict.insert(key.to_string(), value.to_string());            
        }
    }

    // bail out if no host is set
    if host != true {
        return "No Host in your query. Please specify /add?host=hostname&value=some_value.";
        }


    println!("last kvdata {:?}", arg_dict);
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

        for (key, value) in arg_dict {
            
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
    rocket::ignite().mount("/", routes![add, dump]).launch();

}