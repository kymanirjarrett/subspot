from pathlib import Path

import pytest

SAMPLE_CSV = """Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR,PSH,PSD,PSA,PSCH,PSCD,PSCA
E0,16/08/2024,20:00,Man United,Fulham,1,0,H,1.60,4.20,5.50,1.62,4.10,5.40
E0,17/08/2024,12:30,Ipswich,Liverpool,0,2,A,6.50,4.60,1.50,6.80,4.70,1.48
E0,17/08/2024,15:00,Arsenal,Wolves,2,0,H,1.25,6.50,12.00,1.24,6.60,12.50
E0,18/08/2024,16:30,Chelsea,Man City,0,2,A,3.90,3.90,1.90,4.00,3.90,1.88
E0,24/08/2024,15:00,Nott'm Forest,Southampton,1,0,H,2.10,3.40,3.70,2.05,3.45,3.80
E0,24/08/2024,17:30,Brighton,Man United,2,1,H,2.40,3.50,2.90,2.45,3.55,2.80
E0,31/08/2024,15:00,Fulham,Leicester,2,1,H,1.95,3.60,4.00,1.90,3.70,4.10
E0,31/08/2024,15:00,Liverpool,Arsenal,,,,2.40,3.60,2.80,,,
"""


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "E0.csv"
    path.write_text(SAMPLE_CSV, encoding="latin-1")
    return path
