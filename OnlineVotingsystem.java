package CA3;

import javax.swing.*;
import java.awt.Color;
import javax.swing.border.EmptyBorder;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagLayout;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class OnlineVotingsystem {

    static class Candidate {
        String name;
        int votes;

        Candidate(String name) {
            this.name = name;
            this.votes = 0;
        }
    }

    static HashMap<Integer, Candidate> candidates = new HashMap<>();
    static Set<String> votedUsers = new HashSet<>();
    static int candidateIdCounter = 1;

    public static void main(String[] args) {
        JFrame frame = new JFrame("Online Voting System");
        frame.setSize(1000, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout(10, 10));
        frame.getContentPane().setBackground(new Color(245, 248, 250));

        Font buttonFont = new Font("Segoe UI", Font.BOLD, 15);
        Font textFont = new Font("Consolas", Font.PLAIN, 13);
        Font activityFont = new Font("SansSerif", Font.ITALIC, 12);

        JPanel leftPanel = new JPanel(new BorderLayout());
        leftPanel.setBackground(new Color(230, 240, 250));

        JPanel buttonPanel = new JPanel();
        buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));
        buttonPanel.setBackground(new Color(230, 240, 250));
        buttonPanel.setBorder(new EmptyBorder(30, 20, 30, 20));

        String[] labels = {"Add Candidate", "View Candidates", "Vote", "Show Results", "Exit"};
        JButton[] buttons = new JButton[labels.length];
        for (int i = 0; i < labels.length; i++) {
            buttons[i] = new JButton(labels[i]);
            buttons[i].setMaximumSize(new Dimension(180, 40));
            buttons[i].setFont(buttonFont);
            buttons[i].setBackground(new Color(70, 130, 180));
            buttons[i].setForeground(Color.WHITE);
            buttons[i].setFocusPainted(false);
            buttons[i].setAlignmentX(Component.CENTER_ALIGNMENT);
            buttons[i].setToolTipText("Click to " + labels[i].toLowerCase());
            buttonPanel.add(buttons[i]);
            buttonPanel.add(Box.createRigidArea(new Dimension(0, 15)));
        }

        JPanel centerAlign = new JPanel(new GridBagLayout());
        centerAlign.setBackground(new Color(230, 240, 250));
        centerAlign.add(buttonPanel);
        leftPanel.add(centerAlign, BorderLayout.CENTER);
        frame.add(leftPanel, BorderLayout.WEST);

        JTextArea output = new JTextArea(7, 50);
        output.setEditable(false);
        output.setFont(textFont);
        output.setBorder(BorderFactory.createTitledBorder("Backend Console"));
        JScrollPane backendScroll = new JScrollPane(output);
        frame.add(backendScroll, BorderLayout.SOUTH);

        JTextArea activityLog = new JTextArea(20, 25);
        activityLog.setEditable(false);
        activityLog.setFont(activityFont);
        activityLog.setBorder(BorderFactory.createTitledBorder("User Activity"));
        JScrollPane activityPane = new JScrollPane(activityLog);
        frame.add(activityPane, BorderLayout.EAST);

        JButton addBtn = buttons[0];
        JButton viewBtn = buttons[1];
        JButton voteBtn = buttons[2];
        JButton resultBtn = buttons[3];
        JButton exitBtn = buttons[4];

        addBtn.addActionListener(e -> {
            String name = JOptionPane.showInputDialog(frame, "Enter Candidate Name:");
            if (name != null && !name.trim().isEmpty()) {
                candidates.put(candidateIdCounter, new Candidate(name.trim()));
                output.append("Candidate '" + name + "' added with ID: " + candidateIdCounter + "\n");
                activityLog.append("Added candidate: " + name + "\n");
                candidateIdCounter++;
            } else {
                output.append("Invalid candidate name!\n");
            }
        });

        viewBtn.addActionListener(e -> {
            if (candidates.isEmpty()) {
                output.append("No candidates registered.\n");
                JOptionPane.showMessageDialog(frame, "No candidates have registered yet.", "Candidates", JOptionPane.INFORMATION_MESSAGE);
            } else {
                StringBuilder sb = new StringBuilder("List of Candidates:\n\n");
                for (Map.Entry<Integer, Candidate> entry : candidates.entrySet()) {
                    sb.append("ID: ").append(entry.getKey())
                      .append(" | Name: ").append(entry.getValue().name).append("\n");
                }
                output.append(sb.toString());
                activityLog.append("Viewed candidate list\n");
                JOptionPane.showMessageDialog(frame, sb.toString(), "Candidates", JOptionPane.INFORMATION_MESSAGE);
            }
        });

        voteBtn.addActionListener(e -> {
            String voter = JOptionPane.showInputDialog(frame, "Enter your name (voter):");
            if (voter == null || voter.trim().isEmpty()) {
                output.append("Invalid voter name!\n");
                return;
            }

            if (votedUsers.contains(voter.toLowerCase())) {
                output.append("You have already voted!\n");
                activityLog.append("Duplicate vote attempt by: " + voter + "\n");
                return;
            }

            if (candidates.isEmpty()) {
                output.append("No candidates to vote for.\n");
                return;
            }

            StringBuilder candidateList = new StringBuilder("Candidates:\n");
            for (Map.Entry<Integer, Candidate> entry : candidates.entrySet()) {
                candidateList.append("ID: ").append(entry.getKey())
                             .append(" | Name: ").append(entry.getValue().name).append("\n");
            }

            String idStr = JOptionPane.showInputDialog(frame, candidateList + "\nEnter Candidate ID to vote:");
            try {
                int id = Integer.parseInt(idStr);
                if (candidates.containsKey(id)) {
                    candidates.get(id).votes++;
                    votedUsers.add(voter.toLowerCase());
                    output.append(voter + " voted for " + candidates.get(id).name + "\n");
                    activityLog.append(voter + " voted for " + candidates.get(id).name + "\n");

                    StringBuilder votersList = new StringBuilder("Vote successful!\n\nVoters so far:\n");
                    for (String v : votedUsers) {
                        votersList.append("- ").append(v).append("\n");
                    }
                    JOptionPane.showMessageDialog(frame, votersList.toString(), "Voting Confirmed", JOptionPane.INFORMATION_MESSAGE);
                } else {
                    output.append("Invalid Candidate ID!\n");
                }
            } catch (Exception ex) {
                output.append("Please enter a valid numeric ID.\n");
            }
        });

        resultBtn.addActionListener(e -> {
            if (candidates.isEmpty()) {
                output.append("No candidates to show results.\n");
                JOptionPane.showMessageDialog(frame, "No candidates to show results.", "Results", JOptionPane.INFORMATION_MESSAGE);
                return;
            }

            output.append("\nVoting Results:\n");

            int maxVotes = 0;
            for (Candidate c : candidates.values()) {
                output.append(c.name + ": " + c.votes + " vote(s)\n");
                maxVotes = Math.max(maxVotes, c.votes);
            }

            List<String> winners = new ArrayList<>();
            for (Candidate c : candidates.values()) {
                if (c.votes == maxVotes && maxVotes > 0) {
                    winners.add(c.name);
                }
            }

            StringBuilder resultSummary = new StringBuilder("Voting Results:\n");
            for (Candidate c : candidates.values()) {
                resultSummary.append(c.name).append(": ").append(c.votes).append(" vote(s)\n");
            }

            if (winners.isEmpty()) {
                resultSummary.append("\nNo votes have been cast yet.");
            } else if (winners.size() == 1) {
                resultSummary.append("\nWinner: ").append(winners.get(0)).append(" with ").append(maxVotes).append(" vote(s)");
            } else {
                resultSummary.append("\nIt's a draw between:\n");
                for (String name : winners) {
                    resultSummary.append("• ").append(name).append("\n");
                }
                resultSummary.append("Each got ").append(maxVotes).append(" vote(s)");
            }

            activityLog.append("Results viewed\n");
            JOptionPane.showMessageDialog(frame, resultSummary.toString(), "Election Results", JOptionPane.INFORMATION_MESSAGE);
        });

        exitBtn.addActionListener(e -> {
            JOptionPane.showMessageDialog(frame, "Thank you for participating!");
            System.exit(0);
        });

        frame.setVisible(true);
    }
}
