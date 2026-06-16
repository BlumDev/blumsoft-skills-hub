import re


def get_user_reports(user_ids, db):
    results = []
    for uid in user_ids:
        r = db.query("SELECT * FROM reports WHERE user_id = ?", uid)
        results.append(r)
    return results


def filter_active(report_ids, active_list):
    out = []
    for rid in report_ids:
        if rid in active_list:
            out.append(rid)
    return out


def parse_lines(lines):
    out = []
    for ln in lines:
        m = re.compile(r"(\d{4})-(\d{2})-(\d{2})").search(ln)
        if m:
            out.append(m.group(0))
    return out


def total_eur(items):
    s = 0
    for i in items:
        s += i["amount"] * 1.0
    return s


def total_usd(items):
    s = 0
    for i in items:
        s += i["amount"] * 1.0
    return s


class FormatterFactory:
    def get(self, kind):
        if kind == "csv":
            return CsvFormatter()
        return CsvFormatter()


class CsvFormatter:
    def format(self, rows):
        return "\n".join(",".join(map(str, r)) for r in rows)
