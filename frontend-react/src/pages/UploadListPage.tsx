import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
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

  const [listName, setListName] = useState('');
  const [listType, setListType] = useState('course');
  const [customType, setCustomType] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState('');
  const [uploadMethod, setUploadMethod] = useState<'file' | 'paste'>('file');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

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
      // Navigate to the created list (assuming API returns the list ID)
      if (result.data?.id) {
        navigate(`/list/${result.data.id}`);
      } else {
        navigate('/');
      }
    } catch (error) {
      console.error('Failed to upload packing list:', error);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Button
          variant="secondary"
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <ArrowLeft className="inline mr-2" size={16} />
          Back to Lists
        </Button>
        <h1 className="text-3xl font-bold text-military-dark">Upload Packing List</h1>
        <p className="text-gray-600 mt-2">
          Upload a file (CSV, Excel, PDF) or paste text to create a packing list
        </p>
      </div>

      <Card>
        <form onSubmit={handleSubmit}>
          <Input
            label="List Name *"
            placeholder="e.g., Ranger School Packing List"
            value={listName}
            onChange={(e) => setListName(e.target.value)}
            required
          />

          <div className="mb-4">
            <label className="block text-sm font-medium text-military-dark mb-1">
              Description
            </label>
            <textarea
              placeholder="Optional description of this packing list"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent transition-colors duration-200"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <Select
            label="List Type *"
            options={PACKING_LIST_TYPES}
            value={listType}
            onChange={(e) => setListType(e.target.value)}
            required
          />

          {listType === 'other' && (
            <Input
              label="Custom Type"
              placeholder="Specify custom type"
              value={customType}
              onChange={(e) => setCustomType(e.target.value)}
            />
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-military-dark mb-3">
              Upload Method *
            </label>
            <div className="flex gap-4 mb-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="uploadMethod"
                  value="file"
                  checked={uploadMethod === 'file'}
                  onChange={() => setUploadMethod('file')}
                  className="text-military-navy"
                />
                <FileText size={20} />
                <span>Upload File</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="uploadMethod"
                  value="paste"
                  checked={uploadMethod === 'paste'}
                  onChange={() => setUploadMethod('paste')}
                  className="text-military-navy"
                />
                <FileText size={20} />
                <span>Paste Text</span>
              </label>
            </div>

            {uploadMethod === 'file' ? (
              <div>
                <label className="block w-full cursor-pointer">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-military-navy transition-colors">
                    <Upload className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-sm text-gray-600 mb-2">
                      {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-xs text-gray-500">
                      CSV, Excel (.xls, .xlsx), or PDF files accepted
                    </p>
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept=".csv,.xls,.xlsx,.pdf"
                    onChange={handleFileChange}
                    required={uploadMethod === 'file'}
                  />
                </label>
              </div>
            ) : (
              <div>
                <textarea
                  placeholder="Paste your packing list text here..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent transition-colors duration-200"
                  rows={10}
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  required={uploadMethod === 'paste'}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Paste a list of items, one per line. Format: Item Name (optional: quantity, notes)
                </p>
              </div>
            )}
          </div>

          <div className="flex gap-4 mt-6">
            <Button
              type="submit"
              variant="success"
              disabled={uploadMutation.isPending}
            >
              {uploadMutation.isPending ? 'Uploading...' : 'Upload & Create List'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/')}
            >
              Cancel
            </Button>
          </div>

          {uploadMutation.isError && (
            <div className="mt-4 p-3 bg-status-required/10 border border-status-required rounded-md">
              <p className="text-sm text-status-required">
                Failed to upload packing list. Please try again.
              </p>
            </div>
          )}
        </form>
      </Card>
    </div>
  );
}
