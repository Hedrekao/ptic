import { serverUrl } from 'app/services/utils';
import Image from 'next/image'

export const ImageGrid = ({ filePaths }: { filePaths: string[] }) => {
  if (!filePaths || filePaths.length === 0) return null;

  if (filePaths.length > 3) {
    filePaths = filePaths.slice(0, 3);
  }

  function getImageSize() {
    if (filePaths.length === 1) {
      return 250;
    } else if (filePaths.length === 2) {
      return 200;
    }
    return 150;
  }


  return (
    <div className={`flex gap-4`}>
      {filePaths.map((path) => (
        <div
          key={path}
          className={`relative overflow-hidden mx-auto`}
        >
          <Image
            src={`${serverUrl}/uploads/${path}`}
            alt="File to manually classify"
            width={getImageSize()}
            height={getImageSize()}
          />
        </div>
      ))}
    </div>
  );
};
