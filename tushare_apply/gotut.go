package main
import("fmt" 
    "math/rand"
    "net/http"
    // "io/ioutil"
    "encoding/xml"
    )

func add (x,y float32) float32{
    return x+y
}

func multiple(a,b string)(string,string){
    return a,b
}

func lesson_syntax(){
    rand.Seed(12)
    fmt.Println(rand.Intn(12))
}

func lesson_type(){
    var num1,num2 float32 = 5.6 ,9.5
    w1, w2 := "Hey","there"
    fmt.Println(add(num1,num2))
    fmt.Println(multiple(w1,w2))
    var a int = 62
    var b float64 = float64(a)
    fmt.Println(b)
}
func lesson_pointer(){
    x := 15
    a := &x
    *a = 5
    *a = *a* *a
    fmt.Println(a)
    fmt.Println(x)   
}

const x int = 5

func index_handler(w http.ResponseWriter, r *http.Request){
    fmt.Fprintf(w, "Whoa, Go is neat\n")
    fmt.Fprintf(w, r.UserAgent())
}

func about_handler(w http.ResponseWriter, r *http.Request){
    fmt.Fprintf(w, "Author is Go")
}

func lesson_simpleweb(){
   http.HandleFunc("/", index_handler)
   http.HandleFunc("/about", about_handler)
   http.ListenAndServe(":8000", nil)
}
type car struct{
    gas_pedal uint16 //min 0 max 65536
    brake_pedal uint16 //min 0 max 65536
    steering_wheel int16 //min 0 max 65536
    top_speed_kmh float64   
}
const usixteenbitmax float64=65535
const kmh_multiple float64 = 1.60934

func (c car) kmh() float64{
    // c.top_speed_kmh=1122
    return float64(c.gas_pedal)*(c.top_speed_kmh/usixteenbitmax)
}

func (c car) mph() float64{
    return float64(c.gas_pedal)*(c.top_speed_kmh/usixteenbitmax)/kmh_multiple
}


func (c *car) change_top_speed(newspeed float64){
    c.top_speed_kmh = newspeed    
}

func lesson_struct_method(){
   a_car := car{gas_pedal:65000,brake_pedal:0,steering_wheel:12561,top_speed_kmh:225.0}
   b_car := car{223,12,12562,225.0}
   
   fmt.Println(a_car.gas_pedal)
   fmt.Println(b_car.brake_pedal)
   
   fmt.Println(a_car.kmh())
   fmt.Println(a_car.mph())
   
   a_car.change_top_speed(500)
   fmt.Println(a_car.kmh())
   fmt.Println(a_car.mph())
   
}


var testXml=[]byte(`
<sitemapindex>
   <sitemap>
      <loc>http://www.washingtonpost.com/news-politics-sitemap.xml</loc>
   </sitemap>
   <sitemap>
      <loc>http://www.washingtonpost.com/news-blogs-politics-sitemap.xml</loc>
   </sitemap>
   <sitemap>
      <loc>http://www.washingtonpost.com/news-opinions-sitemap.xml</loc>
   </sitemap>
</sitemapindex>
`)

var testXmlDetail=[]byte(`
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
	xmlns:n="http://www.google.com/schemas/sitemap-news/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
       http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd
       http://www.google.com/schemas/sitemap-news/0.9
       http://www.google.com/schemas/sitemap-news/0.9/sitemap-news.xsd">
        <url>
			<loc>https://www.washingtonpost.com/business/technology/un-adds-32-items-to-list-of-prohibited-goods-for-north-korea/2017/10/23/5f112818-b812-11e7-9b93-b97043e57a22_story.html</loc>
			<changefreq>hourly</changefreq>
			<n:news>
				<n:publication>
					<n:name>Washington Post</n:name>
					<n:language>en</n:language>
				</n:publication>
				<n:publication_date>2017-10-23T22:12:20Z</n:publication_date>
				<n:title>UN adds 32 items to list of prohibited goods for North Korea</n:title>
				<n:keywords>
					UN-United Nations-North Korea-Sanctions,North Korea,East Asia,Asia,United Nations Security Council,United Nations,Business,General news,Sanctions and embargoes,Foreign policy,International relations,Government and politics,Government policy,Military technology,Technology</n:keywords>
			</n:news>
		</url>
        <url>
			<loc>https://www.washingtonpost.com/business/technology/cisco-systems-buying-broadsoft-for-19-billion-cash/2017/10/23/ae024774-b7f2-11e7-9b93-b97043e57a22_story.html</loc>
			<changefreq>hourly</changefreq>
			<n:news>
				<n:publication>
					<n:name>Washington Post</n:name>
					<n:language>en</n:language>
				</n:publication>
				<n:publication_date>2017-10-23T21:42:14Z</n:publication_date>
				<n:title>Cisco Systems buying BroadSoft for $1.9 billion cash</n:title>
				<n:keywords>
					US-Cisco-BroadSoft-Acquisition,Cisco Systems Inc,Business,Technology,Communication technology</n:keywords>
			</n:news>
		</url>
</urlset>
`)
type SitemapIndex struct{
    Locations []Location `xml:"sitemap"`    
}
type Location struct{
    Loc string `xml:"loc"`
}
func (l Location) String() string{
    return fmt.Sprintf("%s",l.Loc)
}
func lesson_xmlparse(){
    // resp,_ := http.Get("https://www.baidu.com")
    // bytes,_ := ioutil.ReadAll(resp.Body)
    bytes := testXml
    fmt.Println(string(bytes))
    var s SitemapIndex
    xml.Unmarshal(bytes,&s)
    fmt.Println(s.Locations)
    
}
func lesson_loop(){
    for i:=0;i<10;i++{
        fmt.Println(i)
    }
}

type News struct{
    Titles []string `xml:"url>news>title"`
    Keywords []string `xml:"url>news>keywords"`
    Locations []string `xml:"url>loc"`
}

type NewsMap struct{
    Keyword string
    Location string
}
func lesson_mappingdata(){
    news_map := make(map[string]NewsMap)
    bytes := testXmlDetail
    // fmt.Println(string(bytes))
    
    var n News
    xml.Unmarshal(bytes,&n)
    for idx,_:= range n.Titles{
        fmt.Println(idx)
        news_map[n.Titles[idx]]= NewsMap{n.Keywords[idx],n.Locations[idx]}
    }
    fmt.Println(news_map)
    
}
func lesson_map(){
    grades := make(map[string]float32)
    grades["Timmy"]=42
    grades["Jess"]=92
    grades["Sam"]=67
    fmt.Println(grades)
    TimsGrade:=grades["Timmy"]
    fmt.Println(TimsGrade)
    delete(grades,"Timmy")
    fmt.Println(grades)
    for key,value := range grades{
        fmt.Println(key,":",value)
    }
}


func main(){   
    // lesson_struct()
    // lesson_simpleweb()
    // lesson_struct_method()
    // lesson_xmlparse()
    // lesson_map()
    lesson_mappingdata()
}