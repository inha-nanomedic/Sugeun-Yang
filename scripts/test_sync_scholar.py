"""Tests for the publication-count sync added to sync_scholar.py.

These cover only the PURE functions (no network):
  - count_publication_rows: count <tr> rows in the lab homepage table
  - set_publication_count: write the count into the 3 profile-page spots

The network fetch + main() wiring are verified separately via a dry-run on the
real index.html (byte-identity check), not here.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_scholar as s

# Mirrors the lab homepage publication-patent.html row markup (4 columns).
LAB_PAGE = """<html><body><table>
  <tbody>
          <tr><td>Paper A</td><td>Journal A</td><td>2025</td><td><a href="x">DOI</a></td></tr>
          <tr><td>Paper B</td><td>Journal B</td><td>2024</td><td><a href="y">PDF</a></td></tr>
          <tr><td>Paper C</td><td>Journal C</td><td>2023</td><td><a href="z">DOI</a></td></tr>
  </tbody>
</table></body></html>"""

# Mirrors the 3 count spots on the profile index.html, plus a Citations pill
# that MUST stay untouched, plus the "15" shown-count that MUST stay 15.
PROFILE = """      <div class="metrics">
        <div class="metric-pill scholar">
          <span class="v">4,385</span>
          <span class="l">Citations</span>
        </div>
        <div class="metric-pill">
          <span class="v">96</span>
          <span class="l">Publications</span>
        </div>
      </div>
      <li><a href="#publications">Publications <span class="count">(15)</span></a></li>
      <h2>Recent Publications <span class="count">(15 of 96)</span></h2>
        <a href="https://inha-nanomedic.com/publication-patent.html" target="_blank" rel="noopener">View all 96 publications &rarr;</a>"""


def test_count_rows_counts_four_column_tr():
    assert s.count_publication_rows(LAB_PAGE) == 3


def test_count_rows_only_inside_tbody():
    # a stray <tr> outside the tbody must not be counted
    html = ('<tr><td>x</td><td>y</td><td>z</td><td>w</td></tr>'
            '<tbody>\n'
            '          <tr><td>A</td><td>B</td><td>C</td><td>D</td></tr>\n'
            '        </tbody>')
    assert s.count_publication_rows(html) == 1


def test_set_count_updates_publications_pill():
    out = s.set_publication_count(PROFILE, 97)
    assert '<span class="v">97</span>\n          <span class="l">Publications</span>' in out


def test_set_count_updates_heading_total_keeps_shown():
    out = s.set_publication_count(PROFILE, 97)
    assert '(15 of 97)' in out          # total bumped
    assert '(15 of 96)' not in out


def test_set_count_updates_footer_link():
    out = s.set_publication_count(PROFILE, 97)
    assert 'View all 97 publications' in out
    assert 'View all 96 publications' not in out


def test_set_count_leaves_citations_pill_untouched():
    out = s.set_publication_count(PROFILE, 97)
    assert '<span class="v">4,385</span>\n          <span class="l">Citations</span>' in out


def test_set_count_leaves_shown_count_tab_untouched():
    # the tab "(15)" is the number of papers shown, not the total — must stay 15
    out = s.set_publication_count(PROFILE, 97)
    assert 'Publications <span class="count">(15)</span>' in out


def test_set_count_noop_when_already_current():
    # already 96 -> set to 96 -> byte-identical
    assert s.set_publication_count(PROFILE, 96) == PROFILE


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
