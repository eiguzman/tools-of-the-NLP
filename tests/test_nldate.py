import calendar
from datetime import date, timedelta

from nldate import parse


class TestAbsoluteDates:
    def test_iso_format(self) -> None:
        assert parse("2025-12-01") == date(2025, 12, 1)

    def test_us_format_slash(self) -> None:
        assert parse("12/01/2025") == date(2025, 12, 1)

    def test_us_format_dash(self) -> None:
        assert parse("12-01-2025") == date(2025, 12, 1)

    def test_month_day_year(self) -> None:
        assert parse("December 1, 2025") == date(2025, 12, 1)

    def test_month_day_year_ordinal(self) -> None:
        assert parse("December 1st, 2025") == date(2025, 12, 1)

    def test_month_day_year_no_comma(self) -> None:
        assert parse("December 1 2025") == date(2025, 12, 1)

    def test_abbreviated_month(self) -> None:
        assert parse("Dec 1, 2025") == date(2025, 12, 1)

    def test_abbreviated_month_ordinal(self) -> None:
        assert parse("Dec 1st, 2025") == date(2025, 12, 1)

    def test_day_month_year(self) -> None:
        assert parse("1 December 2025") == date(2025, 12, 1)

    def test_day_month_year_ordinal(self) -> None:
        assert parse("1st December 2025") == date(2025, 12, 1)

    def test_single_digit_month(self) -> None:
        assert parse("3/15/2025") == date(2025, 3, 15)


class TestRelativeKeywords:
    def test_today(self) -> None:
        assert parse("today") == date.today()

    def test_tomorrow(self) -> None:
        assert parse("tomorrow") == date.today() + timedelta(days=1)

    def test_yesterday(self) -> None:
        assert parse("yesterday") == date.today() - timedelta(days=1)

    def test_next_week(self) -> None:
        assert parse("next week") == date.today() + timedelta(weeks=1)

    def test_last_week(self) -> None:
        assert parse("last week") == date.today() - timedelta(weeks=1)

    def test_next_month(self) -> None:
        today = date.today()
        m = today.month + 1
        y = today.year
        if m > 12:
            m = 1
            y += 1
        last = calendar.monthrange(y, m)[1]
        expected = date(y, m, min(today.day, last))
        assert parse("next month") == expected

    def test_last_month(self) -> None:
        today = date.today()
        m = today.month - 1
        y = today.year
        if m < 1:
            m = 12
            y -= 1
        last = calendar.monthrange(y, m)[1]
        expected = date(y, m, min(today.day, last))
        assert parse("last month") == expected

    def test_next_year(self) -> None:
        today = date.today()
        last = calendar.monthrange(today.year + 1, today.month)[1]
        expected = date(today.year + 1, today.month, min(today.day, last))
        assert parse("next year") == expected

    def test_last_year(self) -> None:
        today = date.today()
        last = calendar.monthrange(today.year - 1, today.month)[1]
        expected = date(today.year - 1, today.month, min(today.day, last))
        assert parse("last year") == expected


class TestWeekdayReferences:
    def test_next_tuesday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("next Tuesday", today) == date(2025, 12, 2)

    def test_next_wednesday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("next Wednesday", today) == date(2025, 12, 3)

    def test_next_sunday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("next Sunday", today) == date(2025, 12, 7)

    def test_last_monday(self) -> None:
        today = date(2025, 12, 3)
        assert parse("last Monday", today) == date(2025, 12, 1)

    def test_this_friday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("this Friday", today) == date(2025, 12, 5)

    def test_this_monday_today(self) -> None:
        today = date(2025, 12, 1)
        assert parse("this Monday", today) == date(2025, 12, 1)

    def test_standalone_monday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("Monday", today) == date(2025, 12, 1)

    def test_standalone_friday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("Friday", today) == date(2025, 12, 5)

    def test_next_friday_from_thursday(self) -> None:
        today = date(2025, 12, 4)
        assert parse("next Friday", today) == date(2025, 12, 5)

    def test_next_monday_from_friday(self) -> None:
        today = date(2025, 12, 5)
        assert parse("next Monday", today) == date(2025, 12, 8)


class TestRelativeWithOffsets:
    def test_in_3_days(self) -> None:
        today = date(2025, 12, 1)
        assert parse("in 3 days", today) == date(2025, 12, 4)

    def test_3_days_from_now(self) -> None:
        today = date(2025, 12, 1)
        assert parse("3 days from now", today) == date(2025, 12, 4)

    def test_5_days_ago(self) -> None:
        today = date(2025, 12, 10)
        assert parse("5 days ago", today) == date(2025, 12, 5)

    def test_in_2_weeks(self) -> None:
        today = date(2025, 12, 1)
        assert parse("in 2 weeks", today) == date(2025, 12, 15)

    def test_2_weeks_ago(self) -> None:
        today = date(2025, 12, 15)
        assert parse("2 weeks ago", today) == date(2025, 12, 1)

    def test_in_1_month(self) -> None:
        today = date(2025, 12, 1)
        assert parse("in 1 month", today) == date(2026, 1, 1)

    def test_1_month_ago(self) -> None:
        today = date(2025, 12, 1)
        assert parse("1 month ago", today) == date(2025, 11, 1)

    def test_in_1_year(self) -> None:
        today = date(2025, 12, 1)
        assert parse("in 1 year", today) == date(2026, 12, 1)

    def test_1_year_ago(self) -> None:
        today = date(2025, 12, 1)
        assert parse("1 year ago", today) == date(2024, 12, 1)

    def test_in_30_days(self) -> None:
        today = date(2025, 12, 1)
        assert parse("in 30 days", today) == date(2025, 12, 31)


class TestComplexRelative:
    def test_5_days_before_dec_1(self) -> None:
        today = date(2025, 12, 1)
        assert parse("5 days before December 1st, 2025", today) == date(2025, 11, 26)

    def test_3_days_after_yesterday(self) -> None:
        today = date(2025, 12, 5)
        assert parse("3 days after yesterday", today) == date(2025, 12, 7)

    def test_1_year_after_yesterday(self) -> None:
        today = date(2025, 12, 5)
        assert parse("1 year after yesterday", today) == date(2026, 12, 4)

    def test_1_year_and_2_months_after_yesterday(self) -> None:
        today = date(2025, 1, 1)
        assert parse("1 year and 2 months after yesterday", today) == date(2026, 2, 28)

    def test_5_days_before_tomorrow(self) -> None:
        today = date(2025, 12, 5)
        assert parse("5 days before tomorrow", today) == date(2025, 12, 1)

    def test_2_weeks_from_tomorrow(self) -> None:
        today = date(2025, 12, 1)
        assert parse("2 weeks from tomorrow", today) == date(2025, 12, 16)

    def test_2_days_after_next_friday(self) -> None:
        today = date(2025, 12, 1)
        assert parse("2 days after next Friday", today) == date(2025, 12, 7)

    def test_3_days_before_last_monday(self) -> None:
        today = date(2025, 12, 10)
        assert parse("3 days before last Monday", today) == date(2025, 12, 5)


class TestWithCustomToday:
    def test_today_custom(self) -> None:
        today = date(2025, 6, 15)
        assert parse("today", today) == date(2025, 6, 15)

    def test_tomorrow_custom(self) -> None:
        today = date(2025, 6, 15)
        assert parse("tomorrow", today) == date(2025, 6, 16)

    def test_yesterday_custom(self) -> None:
        today = date(2025, 6, 15)
        assert parse("yesterday", today) == date(2025, 6, 14)

    def test_next_monday_custom(self) -> None:
        today = date(2025, 6, 15)
        assert parse("next Monday", today) == date(2025, 6, 16)

    def test_next_tuesday_custom(self) -> None:
        today = date(2025, 6, 15)
        assert parse("next Tuesday", today) == date(2025, 6, 17)

    def test_in_5_days_custom(self) -> None:
        today = date(2025, 6, 15)
        assert parse("in 5 days", today) == date(2025, 6, 20)

    def test_in_10_days_wraps_month(self) -> None:
        today = date(2025, 6, 25)
        assert parse("in 10 days", today) == date(2025, 7, 5)


class TestEdgeCases:
    def test_ordinals_various(self) -> None:
        assert parse("January 2nd, 2025") == date(2025, 1, 2)
        assert parse("January 3rd, 2025") == date(2025, 1, 3)
        assert parse("January 21st, 2025") == date(2025, 1, 21)
        assert parse("January 22nd, 2025") == date(2025, 1, 22)
        assert parse("January 23rd, 2025") == date(2025, 1, 23)
        assert parse("January 24th, 2025") == date(2025, 1, 24)

    def test_leap_year(self) -> None:
        assert parse("2024-02-29") == date(2024, 2, 29)
        assert parse("2023-02-28") == date(2023, 2, 28)

    def test_multi_digit_ordinal(self) -> None:
        assert parse("January 15th, 2025") == date(2025, 1, 15)
        assert parse("15th January 2025") == date(2025, 1, 15)

    def test_end_of_year(self) -> None:
        today = date(2025, 12, 30)
        assert parse("in 3 days", today) == date(2026, 1, 2)

    def test_month_wrap_with_31_days(self) -> None:
        today = date(2025, 1, 31)
        assert parse("in 1 month", today) == date(2025, 2, 28)

    def test_day_after_tomorrow(self) -> None:
        today = date(2025, 12, 1)
        assert parse("day after tomorrow", today) == date(2025, 12, 3)

    def test_day_before_yesterday(self) -> None:
        today = date(2025, 12, 3)
        assert parse("day before yesterday", today) == date(2025, 12, 1)


class TestTodayDefault:
    def test_default_today_is_used(self) -> None:
        result = parse("today")
        assert result == date.today()
