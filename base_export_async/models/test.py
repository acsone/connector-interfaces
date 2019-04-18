# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import json
import operator

from odoo import api, models, _
from odoo.addons.queue_job.job import job
from odoo.addons.web.controllers.main import CSVExport, ExcelExport


_logger = logging.getLogger(__name__)


class DelayExport(models.Model):

    _name = 'delay.export'
    _description = 'Allow to delay the export'

    @api.model
    def delay_export(self, data):
        self.with_delay().export(data)

    @api.multi
    @job
    def export(self, data):
        _logger.info('EXPORT for data: %s', data)

        params = json.loads(data.get('data'))
        export_format = params.get('format')
        raw_data = export_format != 'csv'

        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)

        model = self.env[model].with_context(import_compat=import_compat, **params.get('context', {}))
        records = model.browse(ids) or model.search(domain, offset=0, limit=False, order=False)

        if not model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']

        field_names = [f['name'] for f in fields]
        import_data = records.export_data(field_names, raw_data).get('datas', [])

        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]

        if export_format == 'csv':
            csv = CSVExport()
            result = csv.from_data(columns_headers, import_data)
        else:
            xls = ExcelExport()
            result = xls.from_data(columns_headers, import_data)

        _logger.info("TADAAAAA %s" % result)
