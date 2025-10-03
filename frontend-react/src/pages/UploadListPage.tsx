import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, CheckCircle2, Loader2, FileSpreadsheet, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { useUploadPackingList } from '@/hooks/usePackingListMutations';

const PACKING_LIST_TYPES = [
  { value: 'course', label: 'Course' },
  { value: 'selection', label: 'Selection' },
  { value: 'training', label: 'Training' },
  { value: 'deployment', label: 'Deployment' },
  { value: 'other', label: 'Other' },
];

export function UploadListPage() {
  const navigate = useNavigate();
  const uploadMutation = useUploadPackingList();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [listName, setListName] = useState('');
  const [listType, setListType] = useState('course');
  const [customType, setCustomType] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState('');
  const [uploadMethod, setUploadMethod] = useState<'file' | 'paste'>('file');
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      toast.success(`File "${file.name}" selected`);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      // Check file type
      const validExtensions = ['.csv', '.xls', '.xlsx', '.pdf'];
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

      if (validExtensions.includes(fileExt)) {
        setSelectedFile(file);
        toast.success(`File "${file.name}" selected`);
      } else {
        toast.error('Invalid file type. Please upload CSV, Excel, or PDF files.');
      }
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (ext === 'csv' || ext === 'xls' || ext === 'xlsx') {
      return <FileSpreadsheet className="text-status-complete" size={24} />;
    }
    return <FileText className="text-military-navy" size={24} />;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!listName) {
      toast.error('Please enter a list name');
      return;
    }

    if (uploadMethod === 'file' && !selectedFile) {
      toast.error('Please select a file to upload');
      return;
    }

    if (uploadMethod === 'paste' && !pastedText.trim()) {
      toast.error('Please paste some content');
      return;
    }

    setIsSubmitting(true);

    const formData = new FormData();
    formData.append('list_name', listName);
    formData.append('list_type', listType);
    if (customType) formData.append('custom_type', customType);
    if (description) formData.append('description', description);

    if (uploadMethod === 'file' && selectedFile) {
      formData.append('file', selectedFile);
    } else if (uploadMethod === 'paste' && pastedText) {
      formData.append('pasted_text', pastedText);
    }

    try {
      const result = await uploadMutation.mutateAsync(formData);
      setIsSuccess(true);
      toast.success('Packing list uploaded successfully!');

      // Delay navigation to show success animation
      setTimeout(() => {
        if (result.data?.id) {
          navigate(`/list/${result.data.id}`);
        } else {
          navigate('/');
        }
      }, 800);
    } catch (error) {
      toast.error('Failed to upload packing list. Please try again.');
      console.error('Failed to upload packing list:', error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <Button
          variant="secondary"
          onClick={() => navigate('/')}
          className="mb-4"
          disabled={isSubmitting}
        >
          <ArrowLeft className="inline mr-2" size={16} />
          Back to Lists
        </Button>
        <h1 className="text-3xl font-bold text-military-dark">Upload Packing List</h1>
        <p className="text-gray-600 mt-2">
          Upload a file (CSV, Excel, PDF) or paste text to create a packing list
        </p>
      </div>

      <Card className={`transition-all duration-300 ${isSuccess ? 'border-status-complete bg-status-complete/5' : ''}`}>
        {isSuccess ? (
          <div className="py-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-status-complete/10 rounded-full mb-4">
              <CheckCircle2 className="text-status-complete" size={32} />
            </div>
            <h2 className="text-2xl font-bold text-military-dark mb-2">Upload Complete!</h2>
            <p className="text-gray-600">Processing your packing list...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <Input
              label="List Name *"
              placeholder="e.g., Ranger School Packing List"
              value={listName}
              onChange={(e) => setListName(e.target.value)}
              disabled={isSubmitting}
              required
            />

            <div className="mb-4">
              <label className="block text-sm font-medium text-military-dark mb-1">
                Description
              </label>
              <textarea
                placeholder="Optional description of this packing list"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent transition-colors duration-200 disabled:bg-gray-50 disabled:cursor-not-allowed"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <Select
              label="List Type *"
              options={PACKING_LIST_TYPES}
              value={listType}
              onChange={(e) => setListType(e.target.value)}
              disabled={isSubmitting}
              required
            />

            {listType === 'other' && (
              <Input
                label="Custom Type"
                placeholder="Specify custom type"
                value={customType}
                onChange={(e) => setCustomType(e.target.value)}
                disabled={isSubmitting}
              />
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-military-dark mb-3">
                Upload Method *
              </label>
              <div className="flex gap-4 mb-4">
                <label className={`flex items-center gap-2 cursor-pointer px-4 py-2 rounded-lg border transition-all ${
                  uploadMethod === 'file'
                    ? 'bg-military-navy text-white border-military-navy'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-military-navy'
                }`}>
                  <input
                    type="radio"
                    name="uploadMethod"
                    value="file"
                    checked={uploadMethod === 'file'}
                    onChange={() => setUploadMethod('file')}
                    className="hidden"
                    disabled={isSubmitting}
                  />
                  <Upload size={20} />
                  <span>Upload File</span>
                </label>
                <label className={`flex items-center gap-2 cursor-pointer px-4 py-2 rounded-lg border transition-all ${
                  uploadMethod === 'paste'
                    ? 'bg-military-navy text-white border-military-navy'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-military-navy'
                }`}>
                  <input
                    type="radio"
                    name="uploadMethod"
                    value="paste"
                    checked={uploadMethod === 'paste'}
                    onChange={() => setUploadMethod('paste')}
                    className="hidden"
                    disabled={isSubmitting}
                  />
                  <FileText size={20} />
                  <span>Paste Text</span>
                </label>
              </div>

              {uploadMethod === 'file' ? (
                <div>
                  {selectedFile ? (
                    <div className="border-2 border-status-complete bg-status-complete/5 rounded-lg p-4 mb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getFileIcon(selectedFile.name)}
                          <div>
                            <p className="font-medium text-military-dark">{selectedFile.name}</p>
                            <p className="text-sm text-gray-600">
                              {(selectedFile.size / 1024).toFixed(2)} KB
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => setSelectedFile(null)}
                          className="text-gray-400 hover:text-gray-600 transition-colors"
                          disabled={isSubmitting}
                        >
                          <X size={20} />
                        </button>
                      </div>
                    </div>
                  ) : null}

                  <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`
                      border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
                      ${isDragging
                        ? 'border-military-navy bg-military-navy/5'
                        : selectedFile
                        ? 'border-gray-200 bg-gray-50'
                        : 'border-gray-300 hover:border-military-navy hover:bg-gray-50'
                      }
                      ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    <Upload className={`mx-auto mb-3 ${isDragging ? 'text-military-navy' : 'text-gray-400'}`} size={48} />
                    <p className="text-sm text-gray-600 mb-2 font-medium">
                      {isDragging ? 'Drop file here' : selectedFile ? 'Click to change file' : 'Click or drag and drop'}
                    </p>
                    <p className="text-xs text-gray-500">
                      CSV, Excel (.xls, .xlsx), or PDF files accepted
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".csv,.xls,.xlsx,.pdf"
                    onChange={handleFileChange}
                    disabled={isSubmitting}
                  />
                </div>
              ) : (
                <div>
                  <textarea
                    placeholder="Paste your packing list text here...&#10;&#10;Example:&#10;Army Combat Boots, 2&#10;OCP Uniform, 4&#10;Poncho Liner"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent transition-colors duration-200 disabled:bg-gray-50 disabled:cursor-not-allowed"
                    rows={10}
                    value={pastedText}
                    onChange={(e) => setPastedText(e.target.value)}
                    disabled={isSubmitting}
                  />
                  {pastedText && (
                    <div className="mt-2 flex items-center gap-2">
                      <Badge variant="info" size="sm">
                        {pastedText.split('\n').filter(line => line.trim()).length} lines
                      </Badge>
                      <button
                        type="button"
                        onClick={() => setPastedText('')}
                        className="text-sm text-military-navy hover:underline"
                        disabled={isSubmitting}
                      >
                        Clear
                      </button>
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Paste a list of items, one per line. Format: Item Name, Quantity (optional)
                  </p>
                </div>
              )}
            </div>

            <div className="flex gap-4 mt-6">
              <Button
                type="submit"
                variant="success"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="inline mr-2 animate-spin" size={16} />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="inline mr-2" size={16} />
                    Upload & Create List
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/')}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}
