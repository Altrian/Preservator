from datetime import datetime, timezone
import os
import json
from pathlib import Path
import requests
from typing import Any, Union


CACHE_DIR = 'cache'
_cache = {}

def get(name, url):
    if name in _cache:
        print(f"Using cached data for {name}")
        return _cache[name]
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{name}.json")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched data for {name}")
        _cache[name] = data
        return data
    except requests.RequestException as e:
        print(f"Error fetching data for {name}: {e}")
        if os.path.exists(cache_path):
            print(f"Using cached data for {name} from {cache_path}")
            with open(cache_path, 'r') as f:
                data = json.load(f)
            _cache[name] = data
            return data
        else:
            raise RuntimeError(f"Failed to fetch data for {name} and no cache available") from e

ReportType = dict[str, Any]
ReportInput = Union[ReportType, list[ReportType]]

class Report:
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    report_path = json_dir / 'report.json'
    latest_path = json_dir / 'latest_report.json'

    def __init__(self):
        self.current: list[ReportType] = []

    def append(self, *reports: ReportInput) -> None:
        for report in reports:
            if isinstance(report, dict):
                self.current.append(report)
            elif isinstance(report, list):
                self.current.extend(report)
            else:
                raise TypeError(f"Unsupported type for append: {type(report)}")

    def save(self, path: Path = report_path, latest_path: Path = latest_path) -> tuple[Path, Path]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                all_reports: dict[str, ReportType] = json.load(f)
        else:
            all_reports = {}

        for r in self.current:
            all_reports[r['name']] = {'timestamp': datetime.now(timezone.utc).isoformat(), **r}

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(all_reports, f, ensure_ascii=False, indent=2)

        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(self.current, f, ensure_ascii=False, indent=2)
        
        return path, latest_path
    
    @classmethod
    def singular(cls, *module_reports: ReportInput, path: Path = report_path, latest_path: Path = latest_path) -> None:
        report = cls()
        report.append(*module_reports)
        report.save(path, latest_path)
          