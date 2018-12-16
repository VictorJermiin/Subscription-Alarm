using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Text;
using System.IO;
using Tulpep.NotificationWindow;

namespace WindowsFormsApp1
{
    public partial class Form1 : Form
    {
        const int NAME_MAX_CHARACTERS = 15;
        public bool timerush = false;
        public bool run = false;
        public bool test = true;


        public Form1()
        {
            InitializeComponent();
            //FormClosing += Form1_FormClosing;

            if (System.IO.File.Exists("Date1_File.txt"))
            {
                string[] nameText = System.IO.File.ReadAllLines("Date1_File.txt");
                textBox1.Text = nameText[1];
                dateTimePicker1.Text = nameText[0];
            }
        }




        private void timer_Tick(object sender, EventArgs e)
        {
            if (CheckDate() == true)
            {
                if (Validate())
                {
                    Message();
                }
            }
        }

        private bool CheckDate()
        {
            DateTime dt = DateTime.Now;
            string Date1 = System.IO.File.ReadLines("Date1_File.txt").First();

            if (dt.ToString("dd/MM/yyyy") == Date1)
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        private void textBox_Validating(object sender, CancelEventArgs e)
        {
            e.Cancel = !Validate();
        }

        private bool Validate()
        {
            if (!CheckDate())
            {
                return false;
            }

            string nameText = textBox1.Text;
            if (String.IsNullOrEmpty(nameText))
            {
                MessageBox.Show("I am sorry but the name cannot be empty");
                return false;
            }
            if (nameText.Contains(" "))
            {
                MessageBox.Show("I am sorry but the name cannot contain spaces");
                return false;
            }
            if (nameText.Length > 15)
            {
                MessageBox.Show("I am sorry, but the name cannot have more than" + NAME_MAX_CHARACTERS + "characters");
                return false;
            }

            return true;
        }

        private void Message()
        {
            string[] nameText = System.IO.File.ReadAllLines("Date1_File.txt");

            if (run == true)
            {
                PopupNotifier MePopup = new PopupNotifier();
                MePopup.Image = Properties.Resources.Netflix;
                MePopup.TitleText = nameText[1];
                MePopup.ContentText = "Your subscription runs out soon!";
                MePopup.Popup();
                run = false;
            }
        }





        private void button1_Click(object sender, EventArgs e)
        {
            StreamWriter File = new StreamWriter("Date1_File.txt");
            int d = dateTimePicker1.Value.Day;
            int m = dateTimePicker1.Value.Month;
            int y = dateTimePicker1.Value.Year;
            string D = d.ToString();
            if (D.Length == 1)
            {
                D = ("0" + D);
            }
            string M = m.ToString();
            if (M.Length == 1)
            {
                M = ("0" + M);
            }
            string Date1 = (D + "-" + M + "-" + y);
            string nameText = textBox1.Text;

            File.WriteLine(Date1);
            File.WriteLine(nameText);
            File.Close();
            MessageBox.Show(nameText + " is set to the " + Date1);

            if (!Validate())
            {
                return;
            }

            if (timerush == false)
            {
                Timer timer = new Timer();
                timer.Interval = (1 * 1000); // 10 secs
                timer.Tick += new EventHandler(timer_Tick);
                run = true;
                timer.Start();
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {






        }

        private void button3_Click(object sender, EventArgs e)
        {







        }


        private void dodisthing()
        {
            Form1 mImage = new Form1();
            mImage.ShowInTaskbar = true;
            mImage.TopMost = true;
            mImage.Location = new Point(10, 10);
            mImage.StartPosition = FormStartPosition.Manual;
            mImage.Show();
        }

        private void notifyIcon1_MouseClick(object sender, MouseEventArgs e)
        {
            if (Visible)
            {
                notifyIcon1.Visible = true;
            }
            else
            {
                if (e.Button == MouseButtons.Left)
                {
                    notifyIcon1.Visible = false;
                    dodisthing();
                }
            }
        }

        private void closeToolStripMenuItem_Click(object sender, EventArgs e)
        {
            notifyIcon1.Visible = false;
            Application.Exit();
        }
        private void showToolStripMenuItem_Click(object sender, EventArgs e)
        {
            dodisthing();
        }

        private void Form1_SizeChanged(object sender, EventArgs e)
        {
            if (WindowState == FormWindowState.Minimized)
            {
                notifyIcon1.Visible = true;
                Hide();
                WindowState = FormWindowState.Normal;
            }
            else
            {
                WindowState = FormWindowState.Normal;
            }
        }

        private void Form1_FormClosing_1(object sender, FormClosingEventArgs e)
        {
            notifyIcon1.Visible = true;
            Hide();
            WindowState = FormWindowState.Normal;
            e.Cancel = true;
        }
    }
}