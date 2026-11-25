// Power Query template for the processed CSV files created by scripts/clean_data.py.
// Change the folder path to the project's data/processed directory.
let
    Source = Folder.Files("C:\PATH\TO\India_Agri_Commodity_Prices_Analysis\data\processed"),
    CsvFiles = Table.SelectRows(Source, each Text.Lower([Extension]) = ".csv"),
    Imported = Table.AddColumn(CsvFiles, "Rows", each
        Table.PromoteHeaders(
            Csv.Document([Content], [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
            [PromoteAllScalars = true]
        )
    ),
    Combined = Table.Combine(Imported[Rows]),
    Typed = Table.TransformColumnTypes(Combined, {
        {"State", type text}, {"District", type text}, {"Market", type text},
        {"Commodity", type text}, {"Variety", type text}, {"Grade", type text},
        {"Arrival_Date", type date}, {"Min_Price", type number},
        {"Max_Price", type number}, {"Modal_Price", type number},
        {"Commodity_Code", Int64.Type}
    }, "en-IN"),
    WithYear = Table.AddColumn(Typed, "Year", each Date.Year([Arrival_Date]), Int64.Type),
    WithMonth = Table.AddColumn(WithYear, "Month", each Date.Month([Arrival_Date]), Int64.Type),
    WithMonthName = Table.AddColumn(WithMonth, "Month_Name", each Date.MonthName([Arrival_Date]), type text),
    WithCategory = Table.AddColumn(WithMonthName, "Category", each
        let c = Text.Lower([Commodity]) in
            if Text.Contains(c, "gram") or Text.Contains(c, "dal") or Text.Contains(c, "moong") or Text.Contains(c, "arhar") or Text.Contains(c, "urd") or Text.Contains(c, "masur") or Text.Contains(c, "lentil") or Text.Contains(c, "peas") or Text.Contains(c, "lobia") or Text.Contains(c, "moath") then "Pulses"
            else if Text.Contains(c, "wheat") or Text.Contains(c, "rice") or Text.Contains(c, "maize") or Text.Contains(c, "jowar") or Text.Contains(c, "bajra") or Text.Contains(c, "barley") or Text.Contains(c, "ragi") or Text.Contains(c, "millet") or Text.Contains(c, "paddy") or Text.Contains(c, "soji") then "Grains"
            else if Text.Contains(c, "ginger") or Text.Contains(c, "coriander") or Text.Contains(c, "turmeric") or Text.Contains(c, "pepper") or Text.Contains(c, "jeera") or Text.Contains(c, "cummin") or Text.Contains(c, "chill") or Text.Contains(c, "soanf") or Text.Contains(c, "methi") or Text.Contains(c, "ajwan") or Text.Contains(c, "cinamon") or Text.Contains(c, "clove") or Text.Contains(c, "cardamom") or Text.Contains(c, "bay leaf") then "Spices"
            else if Text.Contains(c, "onion") or Text.Contains(c, "potato") or Text.Contains(c, "brinjal") or Text.Contains(c, "cauliflower") or Text.Contains(c, "tomato") or Text.Contains(c, "garlic") or Text.Contains(c, "cabbage") or Text.Contains(c, "capsicum") or Text.Contains(c, "carrot") or Text.Contains(c, "gourd") or Text.Contains(c, "pumpkin") or Text.Contains(c, "beans") or Text.Contains(c, "cucumber") or Text.Contains(c, "raddish") or Text.Contains(c, "spinach") or Text.Contains(c, "yam") or Text.Contains(c, "beetroot") or Text.Contains(c, "ladies finger") or Text.Contains(c, "lemon") or Text.Contains(c, "lime") or Text.Contains(c, "drumstick") then "Vegetables"
            else if Text.Contains(c, "grape") or Text.Contains(c, "orange") or Text.Contains(c, "pineapple") or Text.Contains(c, "apple") or Text.Contains(c, "banana") or Text.Contains(c, "mango") or Text.Contains(c, "papaya") or Text.Contains(c, "pomegranate") or Text.Contains(c, "guava") or Text.Contains(c, "watermelon") then "Fruits"
            else if Text.Contains(c, "groundnut") or Text.Contains(c, "mustard") or Text.Contains(c, "soyabean") or Text.Contains(c, "soybean") or Text.Contains(c, "sesame") or Text.Contains(c, "sunflower") or Text.Contains(c, "linseed") or Text.Contains(c, "castor") then "Oilseeds"
            else "Other", type text)
in
    WithCategory
