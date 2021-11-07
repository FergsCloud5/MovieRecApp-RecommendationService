import pymysql
import json
import logging
import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        db_connection = pymysql.connect(
            **db_info,
            autocommit=True
        )
        return db_connection

    @classmethod
    def get_full_resource(cls, db_schema, table_name):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()
        return res

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):

        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def get_where_clause_args(cls, template):

        terms = []
        args = []
        offset_str = ""
        limit_str = ""
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k, v in template.items():

                if k in ["limit"]:
                    limit_str += k + " " + v + " "
                elif k in ["offset"]:
                    offset_str += k + " " + v + " "
                else:
                    terms.append(k + "=%s")
                    args.append(v)

            if len(terms) == 0:
                clause = " " + limit_str + " " + offset_str
            else:
                clause = " where " + " AND ".join(terms) \
                         + " " + limit_str + " " + offset_str

        return clause, args

    @classmethod
    def find_by_template(cls, db_schema, table_name, template):

        # set up default params
        default_pagination = {'fields': "*",
                              'limit': '20',
                              'offset': '0'}

        # add terms with "fields", "limit", or "offset" before trying to find where clause
        for key in ["limit", "offset"]:
            if key not in template.keys():
                template[key] = default_pagination[key]

        fields = template.get("fields", "*")
        template.pop("fields", None)

        wc, args = RDBService.get_where_clause_args(template)

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select " + fields + " from " + db_schema + "." + table_name + " " + wc
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        cols = []
        vals = []
        args = []

        for k, v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
                   " " + vals_clause

        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def delete_by_template(cls, db_schema, table_name, template):

        wc, args = RDBService.get_where_clause_args(template)

        sql_stmt = "delete from " + db_schema + "." + table_name + " " + wc
        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def get_prev_attributes(cls, template):

        attributes = {}

        # if no offset given, we have result starting at first resource, no previous page
        if int(template.get("offset", 0)) == 0:
            attributes["offset"] = None
            attributes["limit"] = None
            return attributes
        # if offset exists, but it is smaller than the limit
        # return the offset = 0, limit = limit (or 20, by default)
        elif int(template.get("offset", 0)) <= int(template.get("limit", 20)):
            attributes["offset"] = 0
            attributes["limit"] = int(template.get("limit", 20))
            return attributes
        else:
            # otherwise we have a regular previous page, add limit to offset and give next page
            # ex: If we have offset = 10, limit = 10, next page is:
            #                offset = 20, limit = 10
            #                ^ here we add limit (10) to the offset and keep limit as is
            attributes["offset"] = int(template.get("offset", 0)) - int(template.get("limit", 20))
            attributes["limit"] = int(template.get("limit", 20))

            return attributes

    @classmethod
    def get_next_attributes(cls, template):

        attributes = {"offset": int(template.get("offset", 0)) + int(template.get("limit", 20)),
                      "limit": int(template.get("limit", 20))
                      }

        return attributes
