import json

csv_data = """Team Name,Player Name,Role
Chennai Super Kings,Ruturaj Gaikwad,BAT
Chennai Super Kings,Dewald Brevis,BAT
Chennai Super Kings,Ayush Mhatre,BAT
Chennai Super Kings,Matthew Short,BAT
Chennai Super Kings,Sarfaraz Khan,BAT
Chennai Super Kings,Shivam Dube,AR
Chennai Super Kings,Ramakrishna Ghosh,AR
Chennai Super Kings,Jamie Overton,AR
Chennai Super Kings,Anshul Kamboj,AR
Chennai Super Kings,Prashant Veer,AR
Chennai Super Kings,Zakary Foulkes,AR
Chennai Super Kings,Aman Khan,AR
Chennai Super Kings,MS Dhoni,WK
Chennai Super Kings,Urvil Patel,WK
Chennai Super Kings,Sanju Samson,WK
Chennai Super Kings,Kartik Sharma,WK
Chennai Super Kings,Shreyas Gopal,BOW
Chennai Super Kings,Khaleel Ahmed,BOW
Chennai Super Kings,Gurjapneet Singh,BOW
Chennai Super Kings,Mukesh Choudhary,BOW
Chennai Super Kings,Noor Ahmad,BOW
Chennai Super Kings,Akeal Hosein,BOW
Chennai Super Kings,Matt Henry,BOW
Chennai Super Kings,Rahul Chahar,BOW
Chennai Super Kings,Spencer Johnson,BOW
Delhi Capitals,Karun Nair,BAT
Delhi Capitals,Nitish Rana,BAT
Delhi Capitals,Sameer Rizvi,BAT
Delhi Capitals,David Miller,BAT
Delhi Capitals,Pathum Nissanka,BAT
Delhi Capitals,Sahil Parakh,BAT
Delhi Capitals,Prithvi Shaw,BAT
Delhi Capitals,Ashutosh Sharma,AR
Delhi Capitals,Axar Patel,AR
Delhi Capitals,Ajay Jadav Mandal,AR
Delhi Capitals,Madhav Tiwari,AR
Delhi Capitals,Tripurana Vijay,AR
Delhi Capitals,Auqib Nabi Dar,AR
Delhi Capitals,Abishek Porel,WK
Delhi Capitals,KL Rahul,WK
Delhi Capitals,Tristan Stubbs,WK
Delhi Capitals,Dushmantha Chameera,BOW
Delhi Capitals,Kuldeep Yadav,BOW
Delhi Capitals,Mukesh Kumar,BOW
Delhi Capitals,T Natarajan,BOW
Delhi Capitals,Vipraj Nigam,BOW
Delhi Capitals,Mitchell Starc,BOW
Delhi Capitals,Lungi Ngidi,BOW
Delhi Capitals,Kyle Jamieson,BOW
Gujarat Titans,Shubman Gill,BAT
Gujarat Titans,M Shahrukh Khan,BAT
Gujarat Titans,Sai Sudharsan,BAT
Gujarat Titans,Nishant Sindhu,AR
Gujarat Titans,Rashid Khan,AR
Gujarat Titans,Manav Suthar,AR
Gujarat Titans,Rahul Tewatia,AR
Gujarat Titans,Washington Sundar,AR
Gujarat Titans,Arshad Khan,AR
Gujarat Titans,Ravisrinivasan Sai Kishore,AR
Gujarat Titans,Jason Holder,AR
Gujarat Titans,Anuj Rawat,WK
Gujarat Titans,Jos Buttler,WK
Gujarat Titans,Kumar Kushagra,WK
Gujarat Titans,Glenn Phillips,WK
Gujarat Titans,Tom Banton,WK
Gujarat Titans,Gurnoor Brar,BOW
Gujarat Titans,Mohammed Siraj,BOW
Gujarat Titans,Prasidh Krishna,BOW
Gujarat Titans,Kagiso Rabada,BOW
Gujarat Titans,Jayant Yadav,BOW
Gujarat Titans,Ishant Sharma,BOW
Gujarat Titans,Ashok Sharma,BOW
Gujarat Titans,Luke Wood,BOW
Gujarat Titans,Kulwant Khejroliya,BOW
Royal Challengers Bengaluru,Rajat Patidar,BAT
Royal Challengers Bengaluru,Tim David,BAT
Royal Challengers Bengaluru,Virat Kohli,BAT
Royal Challengers Bengaluru,Devdutt Padikkal,BAT
Royal Challengers Bengaluru,Jacob Bethell,AR
Royal Challengers Bengaluru,Krunal Pandya,AR
Royal Challengers Bengaluru,Venkatesh Iyer,AR
Royal Challengers Bengaluru,Vihaan Malhotra,AR
Royal Challengers Bengaluru,Romario Shepherd,AR
Royal Challengers Bengaluru,Mangesh Yadav,AR
Royal Challengers Bengaluru,Kanishk Chouhan,AR
Royal Challengers Bengaluru,Satvik Deswal,AR
Royal Challengers Bengaluru,Philip Salt,WK
Royal Challengers Bengaluru,Jitesh Sharma,WK
Royal Challengers Bengaluru,Jordan Cox,WK
Royal Challengers Bengaluru,Abhinandan Singh,BOW
Royal Challengers Bengaluru,Josh Hazlewood,BOW
Royal Challengers Bengaluru,Rasikh Salam Dar,BOW
Royal Challengers Bengaluru,Bhuvneshwar Kumar,BOW
Royal Challengers Bengaluru,Suyash Sharma,BOW
Royal Challengers Bengaluru,Swapnil Singh,BOW
Royal Challengers Bengaluru,Nuwan Thushara,BOW
Royal Challengers Bengaluru,Jacob Duffy,BOW
Royal Challengers Bengaluru,Vicky Ostwal,BOW
Punjab Kings,Shreyas Iyer,BAT
Punjab Kings,Priyansh Arya,BAT
Punjab Kings,Pyla Avinash,BAT
Punjab Kings,Harnoor Singh,BAT
Punjab Kings,Nehal Wadhera,BAT
Punjab Kings,Mitchell Owen,AR
Punjab Kings,Musheer Khan,AR
Punjab Kings,Shashank Singh,AR
Punjab Kings,Marcus Stoinis,AR
Punjab Kings,Suryansh Shedge,AR
Punjab Kings,Cooper Connolly,AR
Punjab Kings,Azmatullah Omarzai,AR
Punjab Kings,Marco Jansen,AR
Punjab Kings,Praveen Dubey,AR
Punjab Kings,Prabhsimran Singh,WK
Punjab Kings,Vishnu Vinod,WK
Punjab Kings,Arshdeep Singh,BOW
Punjab Kings,Xavier Bartlett,BOW
Punjab Kings,Yuzvendra Chahal,BOW
Punjab Kings,Lockie Ferguson,BOW
Punjab Kings,Harpreet Brar,BOW
Punjab Kings,Vijaykumar Vyshak,BOW
Punjab Kings,Yash Thakur,BOW
Punjab Kings,Ben Dwarshuis,BOW
Punjab Kings,Vishal Nishad,BOW
Kolkata Knight Riders,Angkrish Raghuvanshi,BAT
Kolkata Knight Riders,Rinku Singh,BAT
Kolkata Knight Riders,Finn Allen,BAT
Kolkata Knight Riders,Rahul Tripathi,BAT
Kolkata Knight Riders,Sarthak Ranjan,BAT
Kolkata Knight Riders,Ramandeep Singh,AR
Kolkata Knight Riders,Anukul Roy,AR
Kolkata Knight Riders,Cameron Green,AR
Kolkata Knight Riders,Rachin Ravindra,AR
Kolkata Knight Riders,Sunil Narine,AR
Kolkata Knight Riders,Daksh Kamra,AR
Kolkata Knight Riders,Tim Seifert,WK
Kolkata Knight Riders,Tejasvi Dahiya,WK
Kolkata Knight Riders,Vaibhav Arora,BOW
Kolkata Knight Riders,Umran Malik,BOW
Kolkata Knight Riders,Varun Chakaravarthy,BOW
Kolkata Knight Riders,Prashant Solanki,BOW
Kolkata Knight Riders,Kartik Tyagi,BOW
Kolkata Knight Riders,Matheesha Pathirana,BOW
Kolkata Knight Riders,Blessing Muzarabani,BOW
Kolkata Knight Riders,Saurabh Dubey,BOW
Kolkata Knight Riders,Navdeep Saini,BOW
Sunrisers Hyderabad,Travis Head,BAT
Sunrisers Hyderabad,Smaran Ravichandran,BAT
Sunrisers Hyderabad,Aniket Verma,BAT
Sunrisers Hyderabad,Abhishek Sharma,AR
Sunrisers Hyderabad,Kamindu Mendis,AR
Sunrisers Hyderabad,Nitish Kumar Reddy,AR
Sunrisers Hyderabad,Liam Livingstone,AR
Sunrisers Hyderabad,Harsh Dubey,AR
Sunrisers Hyderabad,Shivang Kumar,AR
Sunrisers Hyderabad,Ishan Kishan,WK
Sunrisers Hyderabad,Heinrich Klaasen,WK
Sunrisers Hyderabad,Salil Arora,WK
Sunrisers Hyderabad,Brydon Carse,BOW
Sunrisers Hyderabad,Pat Cummins,BOW
Sunrisers Hyderabad,Eshan Malinga,BOW
Sunrisers Hyderabad,Jaydev Unadkat,BOW
Sunrisers Hyderabad,Harshal Patel,BOW
Sunrisers Hyderabad,Zeeshan Ansari,BOW
Sunrisers Hyderabad,Sakib Hussain,BOW
Sunrisers Hyderabad,Omkar Tukaram Tarmale,BOW
Sunrisers Hyderabad,Amit Kumar,BOW
Sunrisers Hyderabad,Praful Hinge,BOW
Sunrisers Hyderabad,Krish Fuletra,BOW
Sunrisers Hyderabad,Shivam Mavi,BOW
Sunrisers Hyderabad,David Payne,BOW
Rajasthan Royals,Shubham Dubey,BAT
Rajasthan Royals,Shimron Hetmyer,BAT
Rajasthan Royals,Yashasvi Jaiswal,BAT
Rajasthan Royals,Vaibhav Sooryavanshi,BAT
Rajasthan Royals,Aman Rao Perala,BAT
Rajasthan Royals,Riyan Parag,AR
Rajasthan Royals,Dasun Shanaka,AR
Rajasthan Royals,Ravindra Jadeja,AR
Rajasthan Royals,Dhruv Jurel,WK
Rajasthan Royals,Lhuan-dre Pretorius,WK
Rajasthan Royals,Donovan Ferreira,WK
Rajasthan Royals,Ravi Singh,WK
Rajasthan Royals,Jofra Archer,BOW
Rajasthan Royals,Nandre Burger,BOW
Rajasthan Royals,Tushar Deshpande,BOW
Rajasthan Royals,Kwena Maphaka,BOW
Rajasthan Royals,Sandeep Sharma,BOW
Rajasthan Royals,Yudhvir Singh Charak,BOW
Rajasthan Royals,Vignesh Puthur,BOW
Rajasthan Royals,Yash Raj Punja,BOW
Rajasthan Royals,Sushant Mishra,BOW
Rajasthan Royals,Ravi Bishnoi,BOW
Rajasthan Royals,Brijesh Sharma,BOW
Rajasthan Royals,Adam Milne,BOW
Rajasthan Royals,Kuldeep Sen,BOW
Lucknow Super Giants,Himmat Singh,BAT
Lucknow Super Giants,Aiden Markram,BAT
Lucknow Super Giants,Akshat Raghuwanshi,BAT
Lucknow Super Giants,Abdul Samad,AR
Lucknow Super Giants,Ayush Badoni,AR
Lucknow Super Giants,Arshin Kulkarni,AR
Lucknow Super Giants,Mitchell Marsh,AR
Lucknow Super Giants,Shahbaz Ahmed,AR
Lucknow Super Giants,Arjun Sachin Tendulkar,AR
Lucknow Super Giants,Wanindu Hasaranga,AR
Lucknow Super Giants,Rishabh Pant,WK
Lucknow Super Giants,Matthew Breetzke,WK
Lucknow Super Giants,Nicholas Pooran,WK
Lucknow Super Giants,Mukul Choudhary,WK
Lucknow Super Giants,Josh Inglis,WK
Lucknow Super Giants,Akash Maharaj Singh,BOW
Lucknow Super Giants,Avesh Khan,BOW
Lucknow Super Giants,Mohammed Shami,BOW
Lucknow Super Giants,Prince Yadav,BOW
Lucknow Super Giants,Mohsin Khan,BOW
Lucknow Super Giants,Digvesh Singh Rathi,BOW
Lucknow Super Giants,Manimaran Siddharth,BOW
Lucknow Super Giants,Mayank Prabhu Yadav,BOW
Lucknow Super Giants,Anrich Nortje,BOW
Lucknow Super Giants,Naman Tiwari,BOW
Mumbai Indians,Rohit Sharma,BAT
Mumbai Indians,Suryakumar Yadav,BAT
Mumbai Indians,Tilak Varma,BAT
Mumbai Indians,Danish Malewar,BAT
Mumbai Indians,Sherfane Rutherford,AR
Mumbai Indians,Hardik Pandya,AR
Mumbai Indians,Raj Bawa,AR
Mumbai Indians,Will Jacks,AR
Mumbai Indians,Mayank Rawat,AR
Mumbai Indians,Corbin Bosch,AR
Mumbai Indians,Mitchell Santner,AR
Mumbai Indians,Shardul Thakur,AR
Mumbai Indians,Atharva Ankolekar,AR
Mumbai Indians,Robin Minz,WK
Mumbai Indians,Ryan Rickelton,WK
Mumbai Indians,Quinton de Kock,WK
Mumbai Indians,Trent Boult,BOW
Mumbai Indians,Ashwani Kumar,BOW
Mumbai Indians,Jasprit Bumrah,BOW
Mumbai Indians,Deepak Chahar,BOW
Mumbai Indians,Mayank Markande,BOW
Mumbai Indians,AM Ghazanfar,BOW
Mumbai Indians,Raghu Sharma,BOW
Mumbai Indians,Mohammed Salahuddin Izhar,BOW
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
        if line.strip().startswith("Team Name"): continue  # skip duplicate headers
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
        f.write("USERS = {}\nDRAFTS = {}\nLOCKED_TEAMS = {}\nBUDGET_LIMIT = 100.0\nMAX_PLAYERS = 11\n")

if __name__ == "__main__":
    run()
