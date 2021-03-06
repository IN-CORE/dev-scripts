package edu.illinois.ncsa.incore.service.fragility.models;

public class PaperReference {
    public String name;
    public String doi;
    public String yearPublished;

    public PaperReference(String name, String yearPublished,  String doi) {
        this.name = name;
        this.doi = doi;
        this.yearPublished = yearPublished;
    }

    public PaperReference(String name) {
        this.name = name;
    }

    public PaperReference(String name, String yearPublished) {
        this.name = name;
        this.yearPublished = yearPublished;
    }
}