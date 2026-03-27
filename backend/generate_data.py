import json

csv_data = """Team Name,Player Name,Role,Credits
Chennai Super Kings,Ruturaj Gaikwad,BAT,9.5
Chennai Super Kings,Dewald Brevis,BAT,8.0
Chennai Super Kings,Ayush Mhatre,BAT,7.0
Chennai Super Kings,Matthew Short,BAT,8.0
Chennai Super Kings,Sarfaraz Khan,BAT,7.5
Chennai Super Kings,Shivam Dube,AR,8.5
Chennai Super Kings,Ramakrishna Ghosh,AR,6.5
Chennai Super Kings,Jamie Overton,AR,8.0
Chennai Super Kings,Anshul Kamboj,AR,7.0
Chennai Super Kings,Prashant Veer,AR,6.5
Chennai Super Kings,Zakary Foulkes,AR,7.0
Chennai Super Kings,Aman Khan,AR,7.0
Chennai Super Kings,MS Dhoni,WK,9.0
Chennai Super Kings,Urvil Patel,WK,7.0
Chennai Super Kings,Sanju Samson,WK,9.5
Chennai Super Kings,Kartik Sharma,WK,6.5
Chennai Super Kings,Shreyas Gopal,BOW,7.5
Chennai Super Kings,Khaleel Ahmed,BOW,8.5
Chennai Super Kings,Gurjapneet Singh,BOW,6.5
Chennai Super Kings,Mukesh Choudhary,BOW,7.5
Chennai Super Kings,Noor Ahmad,BOW,8.0
Chennai Super Kings,Akeal Hosein,BOW,8.0
Chennai Super Kings,Matt Henry,BOW,8.0
Chennai Super Kings,Rahul Chahar,BOW,8.0
Chennai Super Kings,Spencer Johnson,BOW,8.0
Delhi Capitals,Karun Nair,BAT,7.5
Delhi Capitals,Nitish Rana,BAT,8.0
Delhi Capitals,Sameer Rizvi,BAT,7.5
Delhi Capitals,David Miller,BAT,9.0
Delhi Capitals,Pathum Nissanka,BAT,8.5
Delhi Capitals,Sahil Parakh,BAT,6.5
Delhi Capitals,Prithvi Shaw,BAT,8.0
Delhi Capitals,Ashutosh Sharma,AR,8.0
Delhi Capitals,Axar Patel,AR,9.0
Delhi Capitals,Ajay Jadav Mandal,AR,6.5
Delhi Capitals,Madhav Tiwari,AR,6.5
Delhi Capitals,Tripurana Vijay,AR,6.5
Delhi Capitals,Auqib Nabi Dar,AR,6.5
Delhi Capitals,Abishek Porel,WK,8.0
Delhi Capitals,KL Rahul,WK,9.5
Delhi Capitals,Tristan Stubbs,WK,8.5
Delhi Capitals,Dushmantha Chameera,BOW,8.0
Delhi Capitals,Kuldeep Yadav,BOW,9.0
Delhi Capitals,Mukesh Kumar,BOW,8.0
Delhi Capitals,T Natarajan,BOW,8.5
Delhi Capitals,Vipraj Nigam,BOW,6.5
Delhi Capitals,Mitchell Starc,BOW,9.0
Delhi Capitals,Lungi Ngidi,BOW,8.0
Delhi Capitals,Kyle Jamieson,BOW,8.0
Gujarat Titans,Shubman Gill,BAT,10.0
Gujarat Titans,M Shahrukh Khan,BAT,8.0
Gujarat Titans,Sai Sudharsan,BAT,8.5
Gujarat Titans,Nishant Sindhu,AR,7.0
Gujarat Titans,Rashid Khan,AR,10.0
Gujarat Titans,Manav Suthar,AR,7.0
Gujarat Titans,Rahul Tewatia,AR,8.0
Gujarat Titans,Washington Sundar,AR,8.0
Gujarat Titans,Arshad Khan,AR,7.0
Gujarat Titans,Ravisrinivasan Sai Kishore,AR,7.5
Gujarat Titans,Jason Holder,AR,8.0
Gujarat Titans,Anuj Rawat,WK,7.5
Gujarat Titans,Jos Buttler,WK,9.5
Gujarat Titans,Kumar Kushagra,WK,7.0
Gujarat Titans,Glenn Phillips,WK,8.5
Gujarat Titans,Tom Banton,WK,8.0
Gujarat Titans,Gurnoor Brar,BOW,6.5
Gujarat Titans,Mohammed Siraj,BOW,9.0
Gujarat Titans,Prasidh Krishna,BOW,8.0
Gujarat Titans,Kagiso Rabada,BOW,9.0
Gujarat Titans,Jayant Yadav,BOW,7.5
Gujarat Titans,Ishant Sharma,BOW,7.5
Gujarat Titans,Ashok Sharma,BOW,6.5
Gujarat Titans,Luke Wood,BOW,7.5
Gujarat Titans,Kulwant Khejroliya,BOW,7.0
Royal Challengers Bengaluru,Rajat Patidar,BAT,8.5
Royal Challengers Bengaluru,Tim David,BAT,8.5
Royal Challengers Bengaluru,Virat Kohli,BAT,10.5
Royal Challengers Bengaluru,Devdutt Padikkal,BAT,8.0
Royal Challengers Bengaluru,Jacob Bethell,AR,7.5
Royal Challengers Bengaluru,Krunal Pandya,AR,8.0
Royal Challengers Bengaluru,Venkatesh Iyer,AR,8.5
Royal Challengers Bengaluru,Vihaan Malhotra,AR,6.5
Royal Challengers Bengaluru,Romario Shepherd,AR,8.0
Royal Challengers Bengaluru,Mangesh Yadav,AR,6.5
Royal Challengers Bengaluru,Kanishk Chouhan,AR,6.5
Royal Challengers Bengaluru,Satvik Deswal,AR,6.5
Royal Challengers Bengaluru,Philip Salt,WK,9.0
Royal Challengers Bengaluru,Jitesh Sharma,WK,8.0
Royal Challengers Bengaluru,Jordan Cox,WK,7.5
Royal Challengers Bengaluru,Abhinandan Singh,BOW,6.5
Royal Challengers Bengaluru,Josh Hazlewood,BOW,9.0
Royal Challengers Bengaluru,Rasikh Salam Dar,BOW,7.5
Royal Challengers Bengaluru,Bhuvneshwar Kumar,BOW,8.5
Royal Challengers Bengaluru,Suyash Sharma,BOW,7.5
Royal Challengers Bengaluru,Swapnil Singh,BOW,7.0
Royal Challengers Bengaluru,Nuwan Thushara,BOW,8.0
Royal Challengers Bengaluru,Jacob Duffy,BOW,7.5
Royal Challengers Bengaluru,Vicky Ostwal,BOW,7.0
Punjab Kings,Shreyas Iyer,BAT,9.0
Punjab Kings,Priyansh Arya,BAT,7.0
Punjab Kings,Pyla Avinash,BAT,6.5
Punjab Kings,Harnoor Singh,BAT,7.0
Punjab Kings,Nehal Wadhera,BAT,8.0
Punjab Kings,Mitchell Owen,AR,7.0
Punjab Kings,Musheer Khan,AR,7.5
Punjab Kings,Shashank Singh,AR,8.0
Punjab Kings,Marcus Stoinis,AR,9.0
Punjab Kings,Suryansh Shedge,AR,6.5
Punjab Kings,Cooper Connolly,AR,7.5
Punjab Kings,Azmatullah Omarzai,AR,8.5
Punjab Kings,Marco Jansen,AR,8.0
Punjab Kings,Praveen Dubey,AR,7.0
Punjab Kings,Prabhsimran Singh,WK,8.0
Punjab Kings,Vishnu Vinod,WK,7.0
Punjab Kings,Arshdeep Singh,BOW,8.5
Punjab Kings,Xavier Bartlett,BOW,8.0
Punjab Kings,Yuzvendra Chahal,BOW,9.0
Punjab Kings,Lockie Ferguson,BOW,8.0
Punjab Kings,Harpreet Brar,BOW,7.5
Punjab Kings,Vijaykumar Vyshak,BOW,7.5
Punjab Kings,Yash Thakur,BOW,7.5
Punjab Kings,Ben Dwarshuis,BOW,7.5
Punjab Kings,Vishal Nishad,BOW,6.5
Kolkata Knight Riders,Angkrish Raghuvanshi,BAT,7.5
Kolkata Knight Riders,Rinku Singh,BAT,9.0
Kolkata Knight Riders,Finn Allen,BAT,8.0
Kolkata Knight Riders,Rahul Tripathi,BAT,8.0
Kolkata Knight Riders,Sarthak Ranjan,BAT,6.5
Kolkata Knight Riders,Ramandeep Singh,AR,8.0
Kolkata Knight Riders,Anukul Roy,AR,7.0
Kolkata Knight Riders,Cameron Green,AR,9.0
Kolkata Knight Riders,Rachin Ravindra,AR,8.5
Kolkata Knight Riders,Sunil Narine,AR,10.0
Kolkata Knight Riders,Daksh Kamra,AR,6.5
Kolkata Knight Riders,Tim Seifert,WK,8.0
Kolkata Knight Riders,Tejasvi Dahiya,WK,6.5
Kolkata Knight Riders,Vaibhav Arora,BOW,7.5
Kolkata Knight Riders,Umran Malik,BOW,8.0
Kolkata Knight Riders,Varun Chakaravarthy,BOW,9.0
Kolkata Knight Riders,Prashant Solanki,BOW,7.0
Kolkata Knight Riders,Kartik Tyagi,BOW,7.5
Kolkata Knight Riders,Matheesha Pathirana,BOW,9.0
Kolkata Knight Riders,Blessing Muzarabani,BOW,7.5
Kolkata Knight Riders,Saurabh Dubey,BOW,6.5
Kolkata Knight Riders,Navdeep Saini,BOW,7.0
Sunrisers Hyderabad,Travis Head,BAT,10.0
Sunrisers Hyderabad,Smaran Ravichandran,BAT,6.5
Sunrisers Hyderabad,Aniket Verma,BAT,6.5
Sunrisers Hyderabad,Abhishek Sharma,AR,9.0
Sunrisers Hyderabad,Kamindu Mendis,AR,8.0
Sunrisers Hyderabad,Nitish Kumar Reddy,AR,8.0
Sunrisers Hyderabad,Liam Livingstone,AR,8.5
Sunrisers Hyderabad,Harsh Dubey,AR,6.5
Sunrisers Hyderabad,Shivang Kumar,AR,6.5
Sunrisers Hyderabad,Ishan Kishan,WK,9.0
Sunrisers Hyderabad,Heinrich Klaasen,WK,10.0
Sunrisers Hyderabad,Salil Arora,WK,6.5
Sunrisers Hyderabad,Brydon Carse,BOW,7.5
Sunrisers Hyderabad,Pat Cummins,BOW,9.5
Sunrisers Hyderabad,Eshan Malinga,BOW,6.5
Sunrisers Hyderabad,Jaydev Unadkat,BOW,7.5
Sunrisers Hyderabad,Harshal Patel,BOW,8.5
Sunrisers Hyderabad,Zeeshan Ansari,BOW,6.5
Sunrisers Hyderabad,Sakib Hussain,BOW,6.5
Sunrisers Hyderabad,Omkar Tukaram Tarmale,BOW,6.5
Sunrisers Hyderabad,Amit Kumar,BOW,6.5
Sunrisers Hyderabad,Praful Hinge,BOW,6.5
Sunrisers Hyderabad,Krish Fuletra,BOW,6.5
Sunrisers Hyderabad,Shivam Mavi,BOW,7.5
Sunrisers Hyderabad,David Payne,BOW,7.5
Rajasthan Royals,Shubham Dubey,BAT,7.0
Rajasthan Royals,Shimron Hetmyer,BAT,8.5
Rajasthan Royals,Yashasvi Jaiswal,BAT,9.5
Rajasthan Royals,Vaibhav Sooryavanshi,BAT,6.5
Rajasthan Royals,Aman Rao Perala,BAT,6.5
Rajasthan Royals,Riyan Parag,AR,8.5
Rajasthan Royals,Dasun Shanaka,AR,8.0
Rajasthan Royals,Ravindra Jadeja,AR,9.5
Rajasthan Royals,Dhruv Jurel,WK,8.0
Rajasthan Royals,Lhuan-dre Pretorius,WK,7.0
Rajasthan Royals,Donovan Ferreira,WK,7.5
Rajasthan Royals,Ravi Singh,WK,6.5
Rajasthan Royals,Jofra Archer,BOW,9.0
Rajasthan Royals,Nandre Burger,BOW,8.0
Rajasthan Royals,Tushar Deshpande,BOW,8.0
Rajasthan Royals,Kwena Maphaka,BOW,7.5
Rajasthan Royals,Sandeep Sharma,BOW,8.0
Rajasthan Royals,Yudhvir Singh Charak,BOW,7.0
Rajasthan Royals,Vignesh Puthur,BOW,6.5
Rajasthan Royals,Yash Raj Punja,BOW,6.5
Rajasthan Royals,Sushant Mishra,BOW,6.5
Rajasthan Royals,Ravi Bishnoi,BOW,8.5
Rajasthan Royals,Brijesh Sharma,BOW,6.5
Rajasthan Royals,Adam Milne,BOW,7.5
Rajasthan Royals,Kuldeep Sen,BOW,7.5
Lucknow Super Giants,Himmat Singh,BAT,7.0
Lucknow Super Giants,Aiden Markram,BAT,9.0
Lucknow Super Giants,Akshat Raghuwanshi,BAT,6.5
Lucknow Super Giants,Abdul Samad,AR,8.0
Lucknow Super Giants,Ayush Badoni,AR,8.0
Lucknow Super Giants,Arshin Kulkarni,AR,7.5
Lucknow Super Giants,Mitchell Marsh,AR,9.0
Lucknow Super Giants,Shahbaz Ahmed,AR,8.0
Lucknow Super Giants,Arjun Sachin Tendulkar,AR,7.0
Lucknow Super Giants,Wanindu Hasaranga,AR,9.0
Lucknow Super Giants,Rishabh Pant,WK,9.5
Lucknow Super Giants,Matthew Breetzke,WK,7.5
Lucknow Super Giants,Nicholas Pooran,WK,10.0
Lucknow Super Giants,Mukul Choudhary,WK,6.5
Lucknow Super Giants,Josh Inglis,WK,8.5
Lucknow Super Giants,Akash Maharaj Singh,BOW,6.5
Lucknow Super Giants,Avesh Khan,BOW,8.0
Lucknow Super Giants,Mohammed Shami,BOW,9.0
Lucknow Super Giants,Prince Yadav,BOW,6.5
Lucknow Super Giants,Mohsin Khan,BOW,8.0
Lucknow Super Giants,Digvesh Singh Rathi,BOW,6.5
Lucknow Super Giants,Manimaran Siddharth,BOW,7.5
Lucknow Super Giants,Mayank Prabhu Yadav,BOW,8.0
Lucknow Super Giants,Anrich Nortje,BOW,8.5
Lucknow Super Giants,Naman Tiwari,BOW,6.5
Mumbai Indians,Rohit Sharma,BAT,9.5
Mumbai Indians,Suryakumar Yadav,BAT,10.5
Mumbai Indians,Tilak Varma,BAT,8.5
Mumbai Indians,Danish Malewar,BAT,6.5
Mumbai Indians,Sherfane Rutherford,BAT,8.0
Mumbai Indians,Hardik Pandya,AR,10.0
Mumbai Indians,Raj Bawa,AR,7.0
Mumbai Indians,Will Jacks,AR,8.5
Mumbai Indians,Mayank Rawat,AR,6.5
Mumbai Indians,Corbin Bosch,AR,7.5
Mumbai Indians,Mitchell Santner,AR,8.0
Mumbai Indians,Shardul Thakur,AR,8.0
Mumbai Indians,Atharva Ankolekar,AR,6.5
Mumbai Indians,Robin Minz,WK,7.0
Mumbai Indians,Ryan Rickelton,WK,8.0
Mumbai Indians,Quinton de Kock,WK,9.0
Mumbai Indians,Trent Boult,BOW,9.0
Mumbai Indians,Ashwani Kumar,BOW,6.5
Mumbai Indians,Jasprit Bumrah,BOW,10.5
Mumbai Indians,Deepak Chahar,BOW,8.0
Mumbai Indians,Mayank Markande,BOW,7.5
Mumbai Indians,AM Ghazanfar,BOW,7.5
Mumbai Indians,Raghu Sharma,BOW,6.5
Mumbai Indians,Mohammed Salahuddin Izhar,BOW,6.5
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
        team, name, role, credits_str = line.split(",")
        team = team.strip()
        name = name.strip()
        role = role.strip()
        credits_val = float(credits_str.strip())
        
        if role == "BOW":
            role = "BOWL"
            
        abbr = TEAMS_MAP[team]
        
        players.append({
            "id": pid,
            "name": name,
            "role": role,
            "team": abbr,
            "credits": credits_val
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
