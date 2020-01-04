# Simple Python module for retrieving available snapshots of an 
# website in a web archive as csv.
#
# Copyright (C) 2019 Marcus Burkhardt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, Markup

import time_machine as tm



# from app import app
app = Flask('flask_app')


@app.route('/', methods=['GET', 'POST'])
def page():
    search_parameters = ''
    results_headline = ''

    tool_name = 'Web Archive Availabilities'
    tool_description = Markup(
        f'<p>This tool allows you to retrieve a list of available archival snapshots for a given URL including subpages and subdomains. By default subpages of a domain are included. Uncheck the box "Include Subpages" to retrieve only exact matches.</p>'
        f'<p>You can filter redirects and revisits from the results. Revisits are indicators that a page has been crawled again, but did not change.</p>'
        f'<p>By entering a start date and/or end date you can limit the scope of your search.</p>')

    query = request.form.get('query', '')
    include_subdomains = request.form.get('include_subdomains', '')
    include_subpages = request.form.get('include_subpages', '')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    filter_redirects = request.form.get('filter_redirects', '')
    filter_revisits = request.form.get('filter_revisits', '')
    

    if include_subpages:
        include_subpages = 'subpages'
    
    ia = tm.Archive()

    fnp1 = datetime.now().strftime('%Y%m%d-%H%M%S')
    fnp2 = re.sub(r'\W', '_', query if query else '_')
    fnp3 = re.sub(r'\W', '_', 'subpages_included' if include_subpages else '_')
    fnp4 = re.sub(r'\W', '_', 'subdomains_included' if include_subdomains else '_')
    fnp5 = re.sub(r'\W', '_', 'redirects_filtered' if filter_redirects else '_')
    fnp6 = re.sub(r'\W', '_', 'revisits_filtered' if filter_revisits else '_')
    fnp7 = re.sub(r'\W', '_', start_date if start_date else '_')
    fnp8 = re.sub(r'\W', '_', end_date if end_date else '_')
    csv_file_name = f'waa-{fnp1}-{fnp2}-{fnp3}-{fnp4}-{fnp5}-{fnp6}-{fnp7}-{fnp8}.csv'

    outpath = os.path.join('static', 'downloads')

    if not os.path.isdir(outpath):
        os.makedirs(outpath)

    csv_download_link = os.path.join(outpath, csv_file_name)
    
    if query:
        if include_subpages:
            include_subpages=True
        else:
            include_subpages=False
        if include_subdomains:
            include_subdomains=True
        else:
            include_subdomains=False
        if filter_redirects:
            filter_redirects=True
        else:
            filter_redirects=False
        if filter_revisits:
            filter_revisits=True
        else:
            filter_revisits=False

        diversify_intervals = False
        diversify_all = False
        
        results = ia.query(query, include_subpages=include_subpages, include_subdomains=include_subdomains, 
            start_date=start_date, end_date=end_date, 
            filter_redirects=filter_redirects, filter_revisits=filter_revisits)

        search_parameters = Markup(
            f'<p>Search parameters:</p><ul>'
            f'<li>Search query: {query}</li>'
            f'<li>Include Subdomains: {include_subdomains}</li>'
            f'<li>Include Subpages: {include_subpages}</li>'
            f'<li>Start date: {start_date}</li>'
            f'<li>End date: {end_date}</li>'
            f'<li>Filter Revisits: {filter_revisits}</li>'
            f'<li>Filter Redirects: {filter_redirects}</li></ul>')

    else:
        results = None

    if type(results) == pd.DataFrame:
        results.to_csv(csv_download_link, sep='\t', index=None)
        results_view = f'{len(results)} samples retrieved.'
        csv_download_link = Markup(
            f'<p><a href="{csv_download_link}">Download results.</a></p>')

    else:
        results_view = ''
        csv_download_link = ''

    if type(results) == pd.DataFrame or len(search_parameters) > 0:
        results_headline = Markup('<h3>Results</h3>')

    return render_template(
        'web-archive-availabilities.html', tool_name=tool_name, tool_description=tool_description, query=query, 
        include_subdomains=include_subdomains, include_subpages=include_subpages,
        start_date=start_date, end_date=end_date, filter_revisits=filter_revisits, filter_redirects=filter_redirects,
        results_headline=results_headline, results=results_view, search_parameters=search_parameters,
        csv_download_link=csv_download_link)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8048)
