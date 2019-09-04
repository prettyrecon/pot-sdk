namespace argos_pbtail
{
    partial class fmMain
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.cpb = new CircularProgressBar.CircularProgressBar();
            this.log1 = new System.Windows.Forms.Label();
            this.log2 = new System.Windows.Forms.Label();
            this.log3 = new System.Windows.Forms.Label();
            this.tm = new System.Windows.Forms.Timer(this.components);
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.bgw1 = new System.ComponentModel.BackgroundWorker();
            this.bgw2 = new System.ComponentModel.BackgroundWorker();
            this.bgw3 = new System.ComponentModel.BackgroundWorker();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            this.SuspendLayout();
            // 
            // cpb
            // 
            this.cpb.AnimationFunction = WinFormAnimation.KnownAnimationFunctions.Liner;
            this.cpb.AnimationSpeed = 500;
            this.cpb.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(222)))), ((int)(((byte)(207)))), ((int)(((byte)(199)))));
            this.cpb.Font = new System.Drawing.Font("Gulim", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.cpb.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(64)))), ((int)(((byte)(64)))), ((int)(((byte)(64)))));
            this.cpb.InnerColor = System.Drawing.Color.FromArgb(((int)(((byte)(222)))), ((int)(((byte)(207)))), ((int)(((byte)(199)))));
            this.cpb.InnerMargin = 2;
            this.cpb.InnerWidth = -1;
            this.cpb.Location = new System.Drawing.Point(900, 591);
            this.cpb.MarqueeAnimationSpeed = 2000;
            this.cpb.Name = "cpb";
            this.cpb.OuterColor = System.Drawing.Color.LightSteelBlue;
            this.cpb.OuterMargin = -25;
            this.cpb.OuterWidth = 26;
            this.cpb.ProgressColor = System.Drawing.Color.Firebrick;
            this.cpb.ProgressWidth = 10;
            this.cpb.SecondaryFont = new System.Drawing.Font("Gulim", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.cpb.Size = new System.Drawing.Size(120, 110);
            this.cpb.StartAngle = 270;
            this.cpb.Style = System.Windows.Forms.ProgressBarStyle.Marquee;
            this.cpb.SubscriptColor = System.Drawing.Color.FromArgb(((int)(((byte)(166)))), ((int)(((byte)(166)))), ((int)(((byte)(166)))));
            this.cpb.SubscriptMargin = new System.Windows.Forms.Padding(10, -35, 0, 0);
            this.cpb.SubscriptText = "";
            this.cpb.SuperscriptColor = System.Drawing.Color.FromArgb(((int)(((byte)(166)))), ((int)(((byte)(166)))), ((int)(((byte)(166)))));
            this.cpb.SuperscriptMargin = new System.Windows.Forms.Padding(10, 35, 0, 0);
            this.cpb.SuperscriptText = "";
            this.cpb.TabIndex = 1;
            this.cpb.Text = "cooking...";
            this.cpb.TextMargin = new System.Windows.Forms.Padding(8, 8, 0, 0);
            this.cpb.Value = 30;
            // 
            // log1
            // 
            this.log1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(222)))), ((int)(((byte)(207)))), ((int)(((byte)(199)))));
            this.log1.Font = new System.Drawing.Font("Times New Roman", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.log1.ForeColor = System.Drawing.SystemColors.HotTrack;
            this.log1.Location = new System.Drawing.Point(70, 50);
            this.log1.Name = "log1";
            this.log1.Size = new System.Drawing.Size(1316, 86);
            this.log1.TabIndex = 2;
            this.log1.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // log2
            // 
            this.log2.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(222)))), ((int)(((byte)(207)))), ((int)(((byte)(199)))));
            this.log2.Font = new System.Drawing.Font("Times New Roman", 11F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.log2.ForeColor = System.Drawing.SystemColors.ControlDarkDark;
            this.log2.Location = new System.Drawing.Point(76, 136);
            this.log2.Name = "log2";
            this.log2.Size = new System.Drawing.Size(1310, 86);
            this.log2.TabIndex = 3;
            this.log2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // log3
            // 
            this.log3.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(222)))), ((int)(((byte)(207)))), ((int)(((byte)(199)))));
            this.log3.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.log3.ForeColor = System.Drawing.SystemColors.ControlDark;
            this.log3.Location = new System.Drawing.Point(58, 222);
            this.log3.Name = "log3";
            this.log3.Size = new System.Drawing.Size(1328, 168);
            this.log3.TabIndex = 4;
            this.log3.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // tm
            // 
            this.tm.Interval = 1000;
            this.tm.Tick += new System.EventHandler(this.tm_Tick);
            // 
            // pictureBox1
            // 
            this.pictureBox1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.pictureBox1.Image = global::argos_pbtail.Properties.Resources.POT_LOG;
            this.pictureBox1.Location = new System.Drawing.Point(0, 0);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(1528, 713);
            this.pictureBox1.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
            this.pictureBox1.TabIndex = 0;
            this.pictureBox1.TabStop = false;
            // 
            // bgw1
            // 
            this.bgw1.DoWork += new System.ComponentModel.DoWorkEventHandler(this.bgw1_DoWork);
            // 
            // bgw2
            // 
            this.bgw2.WorkerSupportsCancellation = true;
            this.bgw2.DoWork += new System.ComponentModel.DoWorkEventHandler(this.bgw2_DoWork);
            // 
            // bgw3
            // 
            this.bgw3.WorkerSupportsCancellation = true;
            this.bgw3.DoWork += new System.ComponentModel.DoWorkEventHandler(this.bgw3_DoWork);
            // 
            // fmMain
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(13F, 24F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.SystemColors.ControlLightLight;
            this.ClientSize = new System.Drawing.Size(1528, 713);
            this.Controls.Add(this.log3);
            this.Controls.Add(this.log2);
            this.Controls.Add(this.log1);
            this.Controls.Add(this.cpb);
            this.Controls.Add(this.pictureBox1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.Name = "fmMain";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Load += new System.EventHandler(this.Form1_Load);
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox pictureBox1;
        private CircularProgressBar.CircularProgressBar cpb;
        private System.Windows.Forms.Label log1;
        private System.Windows.Forms.Label log2;
        private System.Windows.Forms.Label log3;
        private System.Windows.Forms.Timer tm;
        private System.ComponentModel.BackgroundWorker bgw1;
        private System.ComponentModel.BackgroundWorker bgw2;
        private System.ComponentModel.BackgroundWorker bgw3;
    }
}

