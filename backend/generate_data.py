import json

csv_data = """Team Name,Player Name,Role
Chennai Super Kings,Ruturaj Gaikwad,BAT
Chennai Super Kings,MS Dhoni,WK
Chennai Super Kings,Ravindra Jadeja,AR
Chennai Super Kings,Matheesha Pathirana,BOW
Chennai Super Kings,Ravichandran Ashwin,AR
Chennai Super Kings,Khaleel Ahmed,BOW
Chennai Super Kings,Rahul Tripathi,BAT
Chennai Super Kings,Sam Curran,AR
Chennai Super Kings,Devon Conway,WK
Chennai Super Kings,Vijay Shankar,AR
Chennai Super Kings,Rachin Ravindra,AR
Chennai Super Kings,Mukesh Choudhary,BOW
Chennai Super Kings,Deepak Hooda,AR
Chennai Super Kings,Jamie Overton,AR
Chennai Super Kings,Shaik Rasheed,BAT
Delhi Capitals,Axar Patel,AR
Delhi Capitals,Kuldeep Yadav,BOW
Delhi Capitals,Tristan Stubbs,WK
Delhi Capitals,Abishek Porel,WK
Delhi Capitals,KL Rahul,WK
Delhi Capitals,Mitchell Starc,BOW
Delhi Capitals,Jake Fraser-McGurk,BAT
Delhi Capitals,Faf du Plessis,BAT
Delhi Capitals,T Natarajan,BOW
Delhi Capitals,Harry Brook,BAT
Delhi Capitals,Mukesh Kumar,BOW
Delhi Capitals,Sameer Rizvi,BAT
Delhi Capitals,Ashutosh Sharma,BAT
Gujarat Titans,Rashid Khan,BOW
Gujarat Titans,Shubman Gill,BAT
Gujarat Titans,Sai Sudharsan,BAT
Gujarat Titans,Rahul Tewatia,AR
Gujarat Titans,Shahrukh Khan,BAT
Gujarat Titans,Kagiso Rabada,BOW
Gujarat Titans,Mohammed Siraj,BOW
Gujarat Titans,Washington Sundar,AR
Gujarat Titans,Prasidh Krishna,BOW
Gujarat Titans,Jos Buttler,WK
Gujarat Titans,Glenn Phillips,WK
Gujarat Titans,Ishan Kishan,WK
Gujarat Titans,Gerald Coetzee,BOW
Kolkata Knight Riders,Rinku Singh,BAT
Kolkata Knight Riders,Varun Chakaravarthy,BOW
Kolkata Knight Riders,Sunil Narine,AR
Kolkata Knight Riders,Andre Russell,AR
Kolkata Knight Riders,Harshit Rana,BOW
Kolkata Knight Riders,Ramandeep Singh,AR
Kolkata Knight Riders,Venkatesh Iyer,AR
Kolkata Knight Riders,Quinton de Kock,WK
Kolkata Knight Riders,Anrich Nortje,BOW
Kolkata Knight Riders,Manish Pandey,BAT
Kolkata Knight Riders,Rahmanullah Gurbaz,WK
Kolkata Knight Riders,Rovman Powell,BAT
Lucknow Super Giants,Nicholas Pooran,WK
Lucknow Super Giants,Ravi Bishnoi,BOW
Lucknow Super Giants,Mayank Yadav,BOW
Lucknow Super Giants,Mohsin Khan,BOW
Lucknow Super Giants,Ayush Badoni,BAT
Lucknow Super Giants,Rishabh Pant,WK
Lucknow Super Giants,David Miller,BAT
Lucknow Super Giants,Aiden Markram,BAT
Lucknow Super Giants,Mitchell Marsh,AR
Lucknow Super Giants,Abdul Samad,BAT
Lucknow Super Giants,Avesh Khan,BOW
Lucknow Super Giants,Akash Deep,BOW
Mumbai Indians,Jasprit Bumrah,BOW
Mumbai Indians,Suryakumar Yadav,BAT
Mumbai Indians,Hardik Pandya,AR
Mumbai Indians,Rohit Sharma,BAT
Mumbai Indians,Tilak Varma,BAT
Mumbai Indians,Trent Boult,BOW
Mumbai Indians,Naman Dhir,AR
Mumbai Indians,Robin Minz,WK
Mumbai Indians,Will Jacks,AR
Mumbai Indians,Ryan Rickelton,WK
Mumbai Indians,Karn Sharma,BOW
Mumbai Indians,Deepak Chahar,BOW
Mumbai Indians,Mitchell Santner,AR
Punjab Kings,Shashank Singh,BAT
Punjab Kings,Prabhsimran Singh,WK
Punjab Kings,Shreyas Iyer,BAT
Punjab Kings,Arshdeep Singh,BOW
Punjab Kings,Yuzvendra Chahal,BOW
Punjab Kings,Marcus Stoinis,AR
Punjab Kings,Glenn Maxwell,AR
Punjab Kings,Nehal Wadhera,BAT
Punjab Kings,Harshal Patel,BOW
Punjab Kings,Aaron Hardie,AR
Punjab Kings,Marco Jansen,AR
Punjab Kings,Piyush Chawla,BOW
Punjab Kings,Josh Inglis,WK
Rajasthan Royals,Sanju Samson,WK
Rajasthan Royals,Yashasvi Jaiswal,BAT
Rajasthan Royals,Riyan Parag,BAT
Rajasthan Royals,Dhruv Jurel,WK
Rajasthan Royals,Shimron Hetmyer,BAT
Rajasthan Royals,Sandeep Sharma,BOW
Rajasthan Royals,Jofra Archer,BOW
Rajasthan Royals,Maheesh Theekshana,BOW
Rajasthan Royals,Wanindu Hasaranga,AR
Rajasthan Royals,Nitish Rana,BAT
Rajasthan Royals,Tushar Deshpande,BOW
Rajasthan Royals,Akash Madhwal,BOW
Rajasthan Royals,Fazalhaq Farooqi,BOW
Royal Challengers Bengaluru,Virat Kohli,BAT
Royal Challengers Bengaluru,Rajat Patidar,BAT
Royal Challengers Bengaluru,Yash Dayal,BOW
Royal Challengers Bengaluru,Phil Salt,WK
Royal Challengers Bengaluru,Jitesh Sharma,WK
Royal Challengers Bengaluru,Liam Livingstone,AR
Royal Challengers Bengaluru,Josh Hazlewood,BOW
Royal Challengers Bengaluru,Rasikh Salam,BOW
Royal Challengers Bengaluru,Suyash Sharma,BOW
Royal Challengers Bengaluru,Krunal Pandya,AR
Royal Challengers Bengaluru,Bhuvneshwar Kumar,BOW
Royal Challengers Bengaluru,Tim David,BAT
Royal Challengers Bengaluru,Devdutt Padikkal,BAT
Sunrisers Hyderabad,Heinrich Klaasen,WK
Sunrisers Hyderabad,Pat Cummins,BOW
Sunrisers Hyderabad,Abhishek Sharma,AR
Sunrisers Hyderabad,Travis Head,BAT
Sunrisers Hyderabad,Nitish Kumar Reddy,AR
Sunrisers Hyderabad,Mohammed Shami,BOW
Sunrisers Hyderabad,Ishan Kishan,WK
Sunrisers Hyderabad,Harshal Patel,BOW
Sunrisers Hyderabad,Rahul Chahar,BOW
Sunrisers Hyderabad,Adam Zampa,BOW
Sunrisers Hyderabad,Abhinav Manohar,BAT
"""

TEAMS_MAP = {
    "Chennai Super Kings": "CSK",
    "Delhi Capitals": "DC",
    "Gujarat Titans": "GT",
    "Kolkata Knight Riders": "KKR",
    "Lucknow Super Giants": "LSG",
    "Mumbai Indians": "MI",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH",
}

def run():
    lines = csv_data.strip().split("\n")[1:] # skip header
    
    players = []
    pid = 1
    for line in lines:
        if not line.strip(): continue
        team, name, role = line.split(",")
        team = team.strip()
        name = name.strip()
        role = role.strip()
        
        if role == "BOW":
            role = "BOWL"
            
        abbr = TEAMS_MAP[team]
        
        base_val = 8.0 + (len(name) % 4) * 0.5
        
        players.append({
            "id": pid,
            "name": name,
            "role": role,
            "team": abbr,
            "credits": float(base_val)
        })
        pid += 1

    with open("c:/Users/ojhav/OneDrive/Desktop/Kric11/backend/app/data.py", "w", encoding="utf-8") as f:
        f.write('"""\nKric11 — Hardcoded player data.\nUpdated for verified 2026 IPL manual roster.\n"""\n\n')
        
        f.write("TEAMS = {\n")
        for k, v in TEAMS_MAP.items():
            f.write(f'    "{v}": "{k}",\n')
        f.write("}\n\n")
        
        f.write("PLAYERS = [\n")
        for p in players:
            f.write(f'    {{"id": {p["id"]}, "name": "{p["name"]}", "role": "{p["role"]}", "team": "{p["team"]}", "credits": {p["credits"]}}},\n')
        f.write("]\n\n")

        f.write("PLAYERS_BY_ID = {p['id']: p for p in PLAYERS}\n\n")
        f.write("USERS = {}\nDRAFTS = {}\nLOCKED_TEAMS = {}\nBUDGET_LIMIT = 100.0\nMAX_PLAYERS = 12\n")

if __name__ == "__main__":
    run()
