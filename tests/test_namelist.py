"""Unit tests for namelist module.

Based on tests class from https://gist.github.com/krischer/4943658.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013

:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
import unittest
from six.moves import StringIO

from nemo_cmd.namelist import namelist2dict


class TestNameList(unittest.TestCase):
    """
    Some very basic test cases.
    """

    def test_simple_group(self):
        """
        Test simple namelist group with values of different types.
        """
        group = (
            "&group\n"
            "    float = 0.75\n"
            "    integer = 700\n"
            "    string = 'test'\n"
            "    truth = .TRUE.\n"
            "    untruth = .FALSE.\n"
            "    lowercase_truth = .true.\n"
            "    lowercase_untruth = .false.\n"
            "    undotted_true = TRUE\n"
            "    undotted_false = FALSE\n"
            "    lowercase_undotted_true = true\n"
            "    lowercase_undotted_false = false\n"
            "/"
        )
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(
            namelist_dict,
            {
                "group": [
                    {
                        "float": 0.75,
                        "integer": 700,
                        "string": "test",
                        "truth": True,
                        "untruth": False,
                        "lowercase_truth": True,
                        "lowercase_untruth": False,
                        "undotted_true": True,
                        "undotted_false": False,
                        "lowercase_undotted_true": True,
                        "lowercase_undotted_false": False,
                    }
                ]
            },
        )

    def test_double_quote_string(self):
        """
        Test simple namelist group with string value enclosed in double quotes.
        """
        group = "&group\n" '    string = "test"\n' "/"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict, {"group": [{"string": "test"}]})

    def test_empty_string(self):
        """
        Test simple namelist group with empty string value.
        """
        group = "&group\n" '    string1 = ""\n' "    string2 = ''\n" "/"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict, {"group": [{"string1": "", "string2": ""}]})

    def test_group_ends_w_amp_end(self):
        """
        Test simple namelist group with &end as end token.
        """
        group = "&group\n" "    float = 0.75\n" "&end"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict, {"group": [{"float": 0.75}]})

    def test_ignore_empty_group(self):
        """
         Ignore empty namelist group.
        """
        group = "&group\n" "&end"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict, {})

    def test_heterogeneous_list(self):
        """
        Test list of heterogeneous values.
        """
        group = "&group\n" "    foo = 0.75, 700, 'test', .TRUE.\n" "/"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict, {"group": [{"foo": [0.75, 700, "test", True]}]})

    def test_array_element_assignment(self):
        """
        Test simple namelist group with assignment to array element.
        """
        group = "&group\n" "    float(1) = 0.75\n" "    float(2) = 0.85\n" "&end"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict, {"group": [{"float": [0.75, 0.85]}]})

    def test_complex_single_line_group(self):
        """
        Tests a rather complex single line group.
        """
        group = "&list a=1, b=1,2 c='12 / !' / "
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(
            namelist_dict, {"list": [{"a": 1, "b": [1, 2], "c": "12 / !"}]}
        )

    def test_complex_multiple_group(self):
        """
        Same as test_complex_single_line_group() just split over lines.
        """
        group = "&list a=1\n" "b=1,2, c='12 / !' /"
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(
            namelist_dict, {"list": [{"a": 1, "b": [1, 2], "c": "12 / !"}]}
        )

    def test_complex_numbers(self):
        """
        Tests complex numbers. Complex number parsing is rather forgiving.
        """
        group = (
            "&complex_group\n"
            "    number_a = (1,2)\n"
            "    number_b = (1.2,3.4)\n"
            "    number_c = (-1.2,0.0)\n"
            "    number_d = (0.0, 1.0)\n"
            "/"
        )

        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(
            namelist_dict,
            {
                "complex_group": [
                    {
                        "number_a": 1.0 + 2.0j,
                        "number_b": 1.2 + 3.4j,
                        "number_c": -1.2 + 0.0j,
                        "number_d": 0.0j + 1.0j,
                    }
                ]
            },
        )

    def test_group_mixed_and_lists(self):
        """
        Tests a real world example.
        """
        group = (
            "&receiver\n"
            "    station ='XX02'\n"
            "    location = 'a'\n"
            "    lon = 12.51\n"
            "    lat = -0.01\n"
            "    depth = 1.0\n"
            "    attributes = 'vx' 'vy' 'vz'\n"
            "    file_name_prefix = './DATA/mess/'\n"
            "    override = .TRUE.\n"
            "/\n"
        )
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(
            namelist_dict,
            {
                "receiver": [
                    {
                        "station": "XX02",
                        "location": "a",
                        "lon": 12.51,
                        "lat": -0.01,
                        "depth": 1.0,
                        "attributes": ["vx", "vy", "vz"],
                        "file_name_prefix": "./DATA/mess/",
                        "override": True,
                    }
                ]
            },
        )

    def test_multiple_groups(self):
        """
        Mixes groups from some of the previous tests.
        """
        group = (
            "&group\n"
            "    float = 0.75\n"
            "    integer = 700\n"
            "    string = 'test'\n"
            "    truth = .TRUE.\n"
            "    untruth = .FALSE.\n"
            "/\n"
            "\n"
            "&list a=1, b=1,2 c='12 / !' / \n"
            "&list a=1\n"
            "b=1,2, c='12 / !' /\n"
            "&receiver\n"
            "    station ='XX02'\n"
            "    location = 'a'\n"
            "    lon = 12.51\n"
            "    lat = -0.01\n"
            "    depth = 1.0\n"
            "    attributes = 'vx' 'vy' 'vz'\n"
            "    file_name_prefix = './DATA/mess/'\n"
            "    override = .TRUE.\n"
            "/\n"
        )
        namelist_dict = namelist2dict(StringIO(group))

        self.assertEqual(
            namelist_dict,
            {
                "group": [
                    {
                        "float": 0.75,
                        "integer": 700,
                        "string": "test",
                        "truth": True,
                        "untruth": False,
                    }
                ],
                "list": [
                    {"a": 1, "b": [1, 2], "c": "12 / !"},
                    {"a": 1, "b": [1, 2], "c": "12 / !"},
                ],
                "receiver": [
                    {
                        "station": "XX02",
                        "location": "a",
                        "lon": 12.51,
                        "lat": -0.01,
                        "depth": 1.0,
                        "attributes": ["vx", "vy", "vz"],
                        "file_name_prefix": "./DATA/mess/",
                        "override": True,
                    }
                ],
            },
        )

    def test_real_world_example(self):
        """
        Tests example from
            http://owen.sj.ca.us/~rk/howto/slides/f90model/slides/namelist.html
        """
        groups = (
            "! can have blank lines and comments in the namelist input file\n"
            "! place these comments between NAMELISTs\n"
            "\n"
            "!\n"
            "! not every compiler supports comments within the namelist\n"
            "!  in particular vastf90/g77 does not\n"
            "!\n"
            "! some will skip NAMELISTs not directly referenced in read\n"
            "!&BOGUS rko=1 /\n"
            "!\n"
            "&TTDATA \n"
            " TTREAL =  1.,\n"
            " TTINTEGER = 2,\n"
            " TTCOMPLEX = (3.,4.), \n"
            " TTCHAR = 'namelist', \n"
            " TTBOOL = .TRUE./\n"
            "&AADATA\n"
            " AAREAL =  1.  1.  2.  3., \n"
            " AAINTEGER = 2 2 3 4, \n"
            " AACOMPLEX = (3.,4.) (3.,4.) (5.,6.) (7.,7.), \n"
            " AACHAR = 'namelist' 'namelist' 'array' ' the lot', \n"
            " AABOOL = .TRUE. .TRUE. .FALSE. .FALSE./\n"
            "&XXDATA \n"
            " XXREAL =  1., \n"
            " XXINTEGER = 2, \n"
            " XXCOMPLEX = (3.,4.)/"
        )
        namelist_dict = namelist2dict(StringIO(groups))
        self.assertEqual(
            namelist_dict,
            {
                "TTDATA": [
                    {
                        "TTREAL": 1.0,
                        "TTINTEGER": 2,
                        "TTCOMPLEX": 3.0 + 4.0j,
                        "TTCHAR": "namelist",
                        "TTBOOL": True,
                    }
                ],
                "AADATA": [
                    {
                        "AAREAL": [1.0, 1.0, 2.0, 3.0],
                        "AAINTEGER": [2, 2, 3, 4],
                        "AACOMPLEX": [3.0 + 4.0j, 3.0 + 4.0j, 5.0 + 6.0j, 7.0 + 7.0j],
                        "AACHAR": ["namelist", "namelist", "array", " the lot"],
                        "AABOOL": [True, True, False, False],
                    }
                ],
                "XXDATA": [{"XXREAL": 1.0, "XXINTEGER": 2, "XXCOMPLEX": 3.0 + 4.0j}],
            },
        )
