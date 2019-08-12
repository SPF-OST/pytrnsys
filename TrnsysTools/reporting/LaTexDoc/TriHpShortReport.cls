%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Short Report Class Form                    v1.0 Jan-12-2010 %%
%% Daniel Carbonell
%% Institut fur Solartechnik SPF, Hochschule für Technik Rapperswil HSR, Switzerland
%% Basic document class for present simulation results.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\LoadClass[11pt,a4paper]{article}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Packages  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{babel}
\usepackage[latin1,utf8]{inputenc}
\usepackage{psfrag}
\usepackage{amsmath}
\usepackage{float}
\usepackage{array}
\usepackage{graphicx}            
\usepackage{color,titlesec}
\usepackage{colortbl}
\usepackage{lscape}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Margins  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\voffset = -1 in
\hoffset = -1 in

\topmargin  = 10 mm
\headheight = 20 mm
\headsep    = 10 mm

\textwidth  = 150 mm 
\textheight = 210 mm

\marginparwidth = 0 mm
\marginparsep   = 0mm
\evensidemargin = 30mm
\oddsidemargin = 30mm

\footskip = 20 mm
 
\setlength{\parindent}{0pt}
\setlength{\parskip}{1ex plus 0.5ex minus 0.2ex}

\definecolor{spfRed}{rgb}{0.,0.,0.}
\def\thickhrule{\textcolor{black}{\hrule height 1pt}}  
     
\renewcommand{\familydefault}{lmss}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%                Title                        %%%             
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewcommand{\@maketitle}{  
 
  \begin{center}
    \textcolor{white}{kkk}\\
 \thickhrule
    \vspace{1cm}
    \textcolor{black}{\textbf{\huge\bfseries{\@reportName}}}\\
\vspace{1cm}
    \textcolor{black}{\huge\bfseries{\@reportSubName}}\\  
    \ProcessOptions*
  \end{center}
  \thickhrule
\vspace{1cm}
\begin{flushleft}
  \textcolor{black}{\bfseries{\@author} }\\
  \vspace{0.1cm}%  
  \textcolor{blue}{ \@address }\\
 \vspace{0.5cm}%  
    \textit{\@reportDate}
  \end{flushleft}  
  \ProcessOptions*
} 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Sections      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\titleformat{\section}{\color{black}\Large\bfseries}{\thesection.}{0.5em}{}[\color{black}]
\titleformat{\subsection}{\color{black}\large\bfseries}{\thesubsection.}{0.5em}{}[\color{black}]


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Captions                 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewcommand{\@makecaption}[2]{%
  \begin{center}

  \sbox\@tempboxa{\normalsize\fontsize{9}{12}\selectfont #1: #2}%
  \ifdim \wd\@tempboxa >\hsize
    \normalsize\fontsize{9}{12}\selectfont #1: #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip
  \end{center}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Headers and footers %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage{fancyheadings}
\def\Header{
\lhead{
%\includegraphics[width=10.0cm]{LOGOTYPE_COMPLETE_BLUE_EULOGO.png}
\includegraphics[width=4.0cm]{TriHpLogo.png}
}
\rhead{
\includegraphics[width=2.0cm]{EU_Flag_320_213.png}
}

}
\def\MainHeader{
\lhead{
\includegraphics[width=4.0cm]{TriHpLogo.png}
}
\rhead{
\includegraphics[width=2.0cm]{EU_Flag_320_213.png}
}
}



\def\Foot{
  \cfoot{}
  \rfoot{
    \thickhrule
    \medskip
    \textcolor{black}{\textbf{\textit{\thepage}}}
  }
}
\def\MainFoot{
  \cfoot{}
  \rfoot{
    \thickhrule
  }
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\reportName{\@ifnextchar[{\@getshortreportName}{\@getreportName}}
\def\@getreportName#1{\gdef\@reportName{#1}\gdef\@shortreportName{#1}}
\def\@getshortreportName[#1]#2{\gdef\@shortreportName{#1}\gdef\@reportName{#2}}

\def\reportSubName{\@ifnextchar[{\@getshortreportSubName}{\@getreportSubName}}
\def\@getreportSubName#1{\gdef\@reportSubName{#1}\gdef\@shortreportSubName{#1}}
\def\@getshortreportSubName[#1]#2{\gdef\@shortreportSubName{#1}\gdef\@reportSubName{#2}}


\def\reportDate{\@ifnextchar[{\@getshortreportDate}{\@getreportDate}}
\def\@getreportDate#1{\gdef\@reportDate{#1}\gdef\@shortreportDate{#1}}
\def\@getshortreportDate[#1]#2{\gdef\@shortreportDate{#1}\gdef\@reportDate{#2}}

\renewcommand{\abstract}[1]{\gdef\@abstract{#1}}

\def\author{\@ifnextchar[{\@getshortauthor}{\@getauthor}}
\def\@getauthor#1{\gdef\@author{#1}\gdef\@shortauthor{#1}}
\def\@getshortauthor[#1]#2{\gdef\@shortauthor{#1}\gdef\@author{#2}}

\newcommand{\address}[1]{\gdef\@address{#1}}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\bibliographystyle{unsrt}
\renewcommand{\refname}{Bibliography}

\newcommand{\ps@front}{

   \renewcommand{\@oddhead}{}%     header blank
   \renewcommand{\@evenhead}{}%    header blank
   \renewcommand{\@oddfoot}{}%     
   \renewcommand{\@evenfoot}{}%     
   \topmargin = 12cm
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\AtBeginDocument{%
  \pagestyle{fancyplain}
  \MainHeader{}
  \MainFoot{}
  \maketitle    
 \let\maketitle\relax
  \Header{}
  \Foot{}  
 % \tableofcontents
 % \newpage
}
