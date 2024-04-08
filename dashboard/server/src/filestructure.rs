use std::path::Path;

pub trait FileModel {}

pub trait StructurizedFile {
    fn path(&self) -> &Path;
    fn model(&self) -> impl FileModel;
}

pub enum DirectoryKind {
    BatchCollectionDir(()),
    BatchDir(()),
    ExperimentDir(()),
    SeriesDir(()),
}

pub enum FileKind {
    BatchConfigFile(()),
    ExperimentConfigFile(()),
    EventDataFile(()),
    RunMetadataFile(()),
    SolverStdoutFile(()),
}

pub enum GeneralFileKind {
    Dir(DirectoryKind),
    File(FileKind),
}
